# 05 · Episode Runtime / API 协议

## 对外 API（建议）

### `POST /episodes/reset`

请求：

```json
{"case_id":"C001","max_turns":5,"seed":42,"simulator_version":"sim-v1","mode":"EVIDENCE_GROUNDED"}
```

响应（Agent 可见）：

```json
{"episode_id":"EP001","turn":0,"done":false,"observation":{"public_profile":{"revenue_change_3m":-0.35,"loan_balance":800000},"conversation":[],"risk_ledger":[],"remaining_turns":5}}
```

只返回 Public Profile。不要把可回答隐藏 Fact 数量、隐藏风险标签、来源等级或后续表现返回给 Agent。

### `POST /episodes/{episode_id}/step`

`ASK` 请求：

```json
{"request_id":"REQ001","turn":1,"action":{"type":"ASK","question":"最大的客户占多少营收？","target_risk_ids":["R01"],"expected_fact_keys":["largest_customer_revenue_share"]}}
```

`STOP` 请求：

```json
{"request_id":"REQ005","turn":5,"action":{"type":"STOP","reason":"剩余信息无法在当前问答预算内核实"}}
```

公开响应：

```json
{"episode_id":"EP001","turn":1,"done":false,"observation":{"speaker":"customer","text":"最大的客户大概占六成。"},"remaining_turns":4}
```

`expected_fact_keys` 是 Agent 意图声明，不是披露权限。`request_id` 用于幂等，重复请求不得消耗两次轮次或获得两次 Reward。

### `GET /episodes/{episode_id}/trace`

仅 Trainer/Verifier/Auditor 可读取完整轨迹（包括私有 Audit）；Agent 仅可读取已披露消息及自己的 Risk Ledger。区分 API 权限或分离存储，不依赖 Agent 遵守自然语言指令来保密。

## 单轮事务的原子顺序

```text
validate ASK/STOP, turn and idempotency
  ├─ STOP → finalize report → terminal reward → done
  └─ ASK  → parse intent
           → retrieve candidates (hard filter + semantic rerank)
           → disclosure plan (authorized facts)
           → generator (allowed claims only)
           → grounding verifier (fallback if unsafe)
           → publish answer + public evidence refs
           → Risk Updater proposes delta
           → State Manager validates/appends events
           → private audit + reward calculation
           → return public observation, trainer consumes reward separately
```

失败时必须区分 `INVALID_ACTION`、`SIMULATOR_ERROR`、`GROUNDING_FAILED`、`NO_RECORD`、`BUDGET_EXHAUSTED`。对环境错误的步骤标记 `sample_valid=false`，一般不计入策略学习；`NO_RECORD` 则是可用的真实观察，但应避免按无价值问题作确定性惩罚。

## 接口与数据版本

`case_schema_version`、`simulator_version`、`policy_version`、`risk_model_version`、`reward_version`、`prompt_version`、`run_seed` 必须写入 Episode Header 便于复现。数据追踪时至少记录源材料 ID、可见时间、模型输出、校验状态和状态变更事件。

## JSON Schema 关系

- [`case-package`](../schemas/case-package.schema.json) 引用 [`fact`](../schemas/fact.schema.json)
- [`episode`](../schemas/episode.schema.json) 引用 [`agent-action`](../schemas/agent-action.schema.json)、[`risk-ledger`](../schemas/risk-ledger.schema.json)、[`simulator-audit`](../schemas/simulator-audit.schema.json)
- [`question-intent`](../schemas/question-intent.schema.json) 与 [`disclosure-plan`](../schemas/disclosure-plan.schema.json) 为模拟器内部协议

Schema 负责结构校验，实际语义校验还需验证引用存在、访问权限、时序、Fact 权限等业务规则。
