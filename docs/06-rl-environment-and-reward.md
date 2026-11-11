# 06 · 多轮 RL 环境与奖励

## POMDP 定义

| 要素 | 定义 |
|---|---|
| `o_t` Observation | Public Profile、已披露历史、当前 Risk Ledger、剩余问题预算 |
| `s_t` Hidden State | 隐藏 QA/摘要事实、来源、可披露状态、评估标签及内部环境状态 |
| `a_t` Action | 一个 `ASK(question)` 或 `STOP` |
| `T` Transition | Simulator 回答 → 事实/披露状态更新 → RiskDelta |
| `r_t` Step Reward | 新的有效信息、正确状态更新与提问成本 |
| `R_T` Terminal Reward | 可靠目标风险质量、证据覆盖、错误排除惩罚 |
| done | Agent STOP 或预算耗尽，异常环境结束另标记为截断 |

## Reward 草案（未校准）

\[
R = \sum_{t=1}^{T} \bigl(\alpha IG_t + \beta U_t - \lambda C_t\bigr) + \gamma Q_T
\]

- `IG_t`：首次披露、可溯源、与风险推理相关的信息；按语义事实去重，不仅按 Fact ID 去重。权重需要专家复核或校准。
- `U_t`：状态更新正确性；无证据从 SUSPECTED 跳到 REJECTED/MITIGATED 应惩罚。
- `C_t`：提问轮数、无意义重复、超长/不合适问题等成本。
- `Q_T`：最终重要风险识别质量、精准度与漏判率（仅可信标签可承担高权重）；也检查错误的逾期判断和无依据风险解除。

**奖励上限不能通过增加负面标签数量获得**；否则模型会倾向过度标记风险。应使用 precision、evidence alignment、calibration 等约束。

## 历史数据不完全覆盖（核心问题）

- `NO_RECORD`：题目没有历史材料可答 ≠ 问题一定低质量。记录 `simulator_coverage=UNKNOWN/LOW`，不能一律按负分处理。
- `GROUNDING_FAILED`：模拟器出现编造/提前披露属于环境错误，不应当成 Agent 的策略失败。
- 存在可靠且独立佐证的风险标签时，才能使用其计算高权重终局准确率。
- 只有 S4 结论、无具体佐证的案例，不应直接进入在线 Rollout 主训练集合。
- 观察到的“客户回答”是历史客户陈述，不等于客观真值。

## 多轨迹训练

固定 Case Package 与披露政策，对同一客户多采样不同问询路径。针对随机模拟回答，固定 Seed、重复试验或用配对评价消除环境噪声。以风险发现、信息覆盖、终局成本及无依据结论筛选优质轨迹。

GRPO 类策略可以按相同案例的多条轨迹做相对比较，具体算法取决于训练平台实现及奖励稳定性。**Policy gradient 应只作用于 Risk Agent 生成动作的 Token**，不能将 Simulator 输出误作为 Agent 训练目标。

## 终止区分

- `AGENT_STOP`：主动结束，有明确最终报告。
- `TURN_BUDGET_EXHAUSTED`：到达回合上限。
- `ENVIRONMENT_TRUNCATED`：模拟器/服务故障截断，需标记有效性。

## 奖励防作弊检查

- Agent 不能在自己的问句里注入假的金额/日期使环境接受该内容。
- 相同信息重复问不应重复得分。
- 只凭客户自述不能“确认”合同真实性或必然回款。
- 判断为高风险且无证据不应获得奖励；错误地排除真实风险也应惩罚。
- RL 不能凭借 Simulator 的固定措辞/回退模板钻漏洞，需不同模拟器版本与真实 QA 留出测试。
