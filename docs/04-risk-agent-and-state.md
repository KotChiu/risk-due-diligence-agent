# 04 · Risk Agent 与风险状态账本

## 单个 Agent 的三个任务

1. **Risk Identification**：初始画像/新观察 → 事实、有依据的风险假设、正面与负面信号。
2. **Question Planning**：风险重要性、剩余未知、可获取性、预期信息价值 → 选一个问题或 STOP。
3. **Risk Updating**：新客户陈述与历史证据 → 新风险、风险状态变化及需进一步核验项。

V1 可使用同一基座模型、多 Prompt/多任务 SFT；调度在 Episode Controller 层实现。

## 三种不可混淆的状态

| 账本 | 状态 | 原则 |
|---|---|---|
| Disclosure | HIDDEN / MENTIONED / DISCLOSED | 已披露不回退隐藏 |
| Evidence | REPORTED / VERIFIED / CONTRADICTED / UNDETERMINED | 客户陈述不是客观证明 |
| Risk | SUSPECTED / EXPLAINED_UNVERIFIED / SUPPORTED / MITIGATED / UNRESOLVED / REJECTED | 风险存在性、严重度、证据强度分开 |

Risk 不应依据模型自报的 `confidence=0.95` 就升级为 SUPPORTED。状态变更的依据必须指向 Agent 当前可见的证据 ID（不是隐藏原始 Fact ID）；运行时可以维护私有 source-ref ↔ public-evidence-ref 映射。

## 事件溯源（Event Sourcing）

每轮保存 `RiskDelta`，由 State Manager 做 schema 检查、重复检测、支持证据引用验证以及状态转换检查。`RiskLedger` Snapshot 可以从事件重建。

事件类型：`ADD`、`UPDATE`、`RESOLVE`。`RESOLVE` 只表示有明确理由将旧风险置为 REJECTED 或 MITIGATED，不删除历史事件。

### 规则

- 旧的客观观察不可因客户解释消失。
- 同一风险已有 ID 则附加新证据并更新状态，不反复新增重复标签。
- 客户“解释”可以把风险变成 EXPLAINED_UNVERIFIED，不自动升级 VERIFIED/MITIGATED。
- 有真实冲突时同时记录支持/反驳证据；需进一步核验，而非盲选最新回答。
- 随时可保留 `UNRESOLVED` 并 STOP，不能因无证据而强制排除风险。

## 风险对象字段

- `risk_id`、`risk_type`、`description`
- `status`、`severity`、`evidence_strength`（三者相互独立）
- `supporting_evidence_ids`、`contradicting_evidence_ids`
- `uncertainties[]`、`reason`
- `first_seen_turn`、`last_updated_turn`

示例见 [`risk-ledger.example.json`](../examples/risk-ledger.example.json)。

## 问题优先级

建议综合风险潜在影响、剩余未知、可验证性、预期信息增益与提问成本；初期用可解释的启发式 + SFT，后续通过多轨迹 RL 优化。禁止“负面标签数量越多越好”的训练目标。

## STOP

Agent 可以在以下条件下提出 STOP：关键风险已问清、进一步问题边际价值低、缺少可获取证据、客户无法提供信息或达到预算。Controller 应将到达 `max_turns` 记作 `TURN_BUDGET_EXHAUSTED`，与主动 `AGENT_STOP` 区分。
