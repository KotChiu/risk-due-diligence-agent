# 03 · Customer Simulator：语义相关披露

## 总原则

**信息披露由 Gate 控制，语言表达由生成模型完成，事实合法性由 Grounding Verifier 核验。** 不能只给 LLM 一个完整客户档案，并要求它自己保密。

## 四阶段执行

1. **Question Parser**：抽取意图、业务域、请求属性、时间范围、实体、具体程度、问题中自带的假设（presuppositions）。
2. **Fact Retriever**：先根据客户 ID、归属、时间、可披露标志硬过滤，再用属性精确匹配、实体和时序匹配、语义检索召回候选事实。
3. **Disclosure Gate**：将候选事实拆为 `primary_fact_ids`、`supporting_fact_ids`、`withheld_fact_ids`，生成只含允许陈述的 DisclosurePlan。
4. **Generator + Verifier**：LLM 用允许事实回答；基于声明抽取、金额/比例/否定校验和证据蕴含判断检查越权和编造；不合格使用模板回退或标记环境错误。

## 匹配分数（仅排序，不代替准入）

\[
S(q,f) = w_s S_{semantic} + w_a S_{attribute} + w_e S_{entity} + w_t S_{temporal}
\]

参数由真实 QA 校准；**禁止把 Agent 动作里的 `expected_fact_keys` 当作权限凭据**，必须从 question 原文重新理解与匹配。

## V1 披露矩阵

| 问题类型 | 典型回答 | 披露限制 |
|---|---|---|
| 宽泛询问原因 | 主要原因 + 一个直接背景因素 | 不无故给出金额、客户占比或完整证据链 |
| 具体数值/日期 | 被问到的数值，保留约数/区间限定 | 不自动披露邻近的精确事实 |
| 部分可回答 | 回答已知部分并说明未掌握其余 | 不能虚构缺失内容 |
| 带错误前提 | 如历史依据允许，纠正错误前提 | 提问中的数字/判断不能作为事实 |
| 没有记录 | 无法确认；私有审计标记 `NO_RECORD` | 不当作 Agent 的确定性策略错误 |
| 明确拒答记录 | 按来源复现不披露行为 | 不能默认所有客户都拒答 |

## 披露状态

- `HIDDEN`：尚未提及；
- `MENTIONED`：某话题已有概述，但精确 Fact 未披露；
- `DISCLOSED`：具体 Fact 已在回答中获得。

同义事实在语义层也要去重，避免多次重复披露同一事实获取新的信息奖励。若客户在后续轮次提供独立验证证据，奖励应属于 Verification 而非重复 Discovery。

## 回答协议（私有中间结果）

`question_intent` → `disclosure_plan` → `candidate_answer` → `simulator_audit`。对应 Schema 与示例位于 `schemas/`、`examples/`。

**严格分离**：Agent 只看回答文本，训练审计可以看 Fact ID 和 source-span；风险结论和未来 Outcome 不得作为生成模型上下文。

## 重点评测

- Grounding Pass Rate、无依据声明率、精确数字保真率
- Premature Disclosure Rate（提前泄露率）
- 同问不同表述的一致性、连续轮次自洽性
- `NO_RECORD` 的召回准确率
- 模拟器错误率在不同案例类型/来源等级下的分布

如果预设候选回答违反事实约束，生成器应被拒绝或降级模板；**不能把该轮当成正常 RL 样本直接使用**。
