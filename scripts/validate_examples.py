#!/usr/bin/env python3
"""Offline JSON Schema + selected business-invariant validation for the demo data."""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError as exc:
    raise SystemExit("Install dependencies: python -m pip install 'jsonschema>=4.20'") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'schemas'
EXAMPLES = ROOT / 'examples'


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def as_time(value: str):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def main():
    schemas = {p.name: load(p) for p in SCHEMAS.glob('*.schema.json')}
    require(len(schemas) == 8, 'Expected 8 JSON Schemas')
    registry = Registry().with_resources(
        [(doc['$id'], Resource.from_contents(doc)) for doc in schemas.values()]
    )
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        print(f'[SCHEMA] {name}')

    pairs = [
        ('case-package.example.json', 'case-package.schema.json'),
        ('question-intent.example.json', 'question-intent.schema.json'),
        ('disclosure-plan.example.json', 'disclosure-plan.schema.json'),
        ('risk-ledger.example.json', 'risk-ledger.schema.json'),
        ('episode.example.json', 'episode.schema.json'),
    ]
    examples = {}
    for filename, schema_name in pairs:
        data = load(EXAMPLES / filename)
        Draft202012Validator(schemas[schema_name], registry=registry).validate(data)
        examples[filename] = data
        print(f'[EXAMPLE] {filename}')

    case = examples['case-package.example.json']
    plan = examples['disclosure-plan.example.json']
    ledger = examples['risk-ledger.example.json']
    episode = examples['episode.example.json']
    facts = case['hidden_facts']
    facts_by_id = {f['fact_id']: f for f in facts}
    require(len(facts_by_id) == len(facts), 'Duplicated fact IDs')
    source_ids = {s['source_id'] for s in case['source_evidence']}
    require(len(source_ids) == len(case['source_evidence']), 'Duplicated source IDs')
    cutoff = as_time(case['cutoff_at'])
    for f in facts:
        source = f['source']
        require(source['source_id'] in source_ids, f"Missing source: {f['fact_id']}")
        require(as_time(f['knowledge_available_at']) <= cutoff,
                f"Historical fact may not have been known at episode start: {f['fact_id']}")
        if f['eligible_for_simulator']:
            require(source['source_grade'] in {'S1','S2'}, f"Non-S1/S2 disclosure: {f['fact_id']}")
            require(f['speaker'] == 'CUSTOMER', f"Non-customer claim: {f['fact_id']}")
            require(f['visibility'] == 'HIDDEN', f"Unhidden/private fact mismatch: {f['fact_id']}")
        if source['source_grade'] in {'S3', 'S4', 'S5'}:
            require(not f['eligible_for_simulator'], f"Evaluator/tool/synthetic fact leaked: {f['fact_id']}")

    allowed = set(plan['primary_fact_ids'] + plan['supporting_fact_ids'])
    withheld = set(plan['withheld_fact_ids'])
    require(allowed.isdisjoint(withheld), 'DisclosurePlan allowed/withheld overlap')
    require(allowed | withheld <= facts_by_id.keys(), 'Unknown Fact ID in DisclosurePlan')
    require(all(facts_by_id[fid]['eligible_for_simulator'] for fid in allowed),
            'DisclosurePlan contains a forbidden fact')
    require(plan['question_id'] == examples['question-intent.example.json']['question_id'],
            'Question intent and disclosure plan refer to different questions')

    require(episode['case_id'] == case['case_id'], 'Case/Episode mismatch')
    require(episode['episode_id'] == ledger['episode_id'], 'Episode/Ledger mismatch')
    steps = episode['steps']
    require([s['turn'] for s in steps] == list(range(1, len(steps)+1)),
            'Non-contiguous episode turn numbering')
    ask_steps = [s for s in steps if s['agent_action']['type'] == 'ASK']
    stop_steps = [s for s in steps if s['agent_action']['type'] == 'STOP']
    require(len(ask_steps) == episode['terminal']['turn_count'], 'ASK count != turn_count')
    require(len(ask_steps) <= episode['config']['max_turns'], 'Exceeded ASK budget')
    require(len(stop_steps) == 1 and steps[-1] is stop_steps[0], 'STOP must be terminal')

    seen_facts = set()
    public_evidence = {'E00'}
    flattened_deltas = []
    reward_sum = 0.0
    for step in steps:
        if step['agent_action']['type'] == 'STOP':
            require(step['public_answer'] is None and step['private_audit'] is None,
                    'STOP unexpectedly generated an answer/audit')
            require(step['done'], 'STOP should mark done')
            continue
        require(not step['done'], 'ASK prematurely ends episode in example')
        audit = step['private_audit']
        require(audit is not None, 'Missing private simulator audit')
        disclosed = set(audit['disclosed_fact_ids'])
        fresh = set(audit['new_fact_ids'])
        require(disclosed <= facts_by_id.keys(), 'Unknown disclosed fact ID')
        require(all(facts_by_id[fid]['eligible_for_simulator'] for fid in disclosed),
                'Private-only/evaluator fact disclosed')
        require(fresh == disclosed - seen_facts, 'Incorrect new fact bookkeeping')
        require(audit['grounding_pass'] and audit['environment_valid'] and not audit['premature_disclosure'],
                'Invalid ground truth example response')
        seen_facts.update(disclosed)
        public_evidence.update(step['public_evidence_ids'])
        for d in step['risk_delta']:
            require(set(d['evidence_ids']) <= public_evidence, 'Risk delta references hidden evidence')
            flattened_deltas.append((step['turn'], d))
        r = step['reward']
        require(r is not None and r['sample_valid'], 'Invalid training reward')
        expected = sum(r[k] for k in ('information_gain','update_quality','risk_discovery','question_cost'))
        require(math.isclose(expected, r['total'], abs_tol=1e-8), 'Reward component sum mismatch')
        reward_sum += r['total']

    events = ledger['events']
    require(ledger['ledger_version'] == len(events), 'Ledger version must match event count')
    require(len(events) == len(flattened_deltas)+1, 'Ledger should contain one initial risk event')
    require(events[0]['turn']==0 and events[0]['delta']['operation']=='ADD', 'Missing initial risk')
    for event, (turn, delta) in zip(events[1:], flattened_deltas):
        require(event['turn']==turn and event['delta']==delta, 'Episode/ledger event mismatch')
    risks = {r['risk_id']: r for r in ledger['risks']}
    for r in ledger['risks']:
        last = [event for event in events if event['delta']['risk_id']==r['risk_id']][-1]
        require(r['status']==last['delta']['new_status'], f"Stale risk status: {r['risk_id']}")
        require(set(r['supporting_evidence_ids']) <= public_evidence,
                f"Risk uses hidden evidence ID: {r['risk_id']}")
    comps = episode['terminal']['reward_components']
    target = reward_sum + sum(comps.values())  # Illustrative version uses unit coefficients
    require(math.isclose(target, episode['terminal']['total_episode_reward'], abs_tol=1e-8),
            'Illustrative terminal reward components do not sum')

    print(f'[SEMANTIC] PASS: {len(facts)} grounded facts, {len(ask_steps)} ASK turns, '
          f'{len(risks)} final risks, {len(events)} state events')
    print('All validations passed.')


if __name__ == '__main__':
    main()
