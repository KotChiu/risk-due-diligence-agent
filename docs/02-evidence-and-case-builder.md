# 02 · 历史证据抽取与 Case Package

## 原始来源到结构化信息

| 来源 | 处理 | 结果 |
|---|---|---|
| 历史 QA | 切分问题、回答、讲话人、原文 span；抽取可证实的“说过什么” | S1 客户陈述 |
| 尽调摘要 | 句子级归因：客户称、经核查、调查员判断、归属不明 | S2 / S3 / S4 / 暂不使用 |
| 结构化结论 | 映射风险 taxonomy，保留标签制作者与根据 | Verifier 标签，通常为 S4 |
| 初始画像 | 记录可见时间、原始指标与计算口径 | Public Profile |
| 贷后结果 | 保留发生时间、观察窗口与标签口径 | 仅离线 Outcome |

### 两个独立维度

**Source grade（来源等级）**：
- `S1`：原始历史 QA 中客户直接陈述；Simulator 可披露。
- `S2`：尽调摘要中有明确“客户称”归属；Simulator 可披露。
- `S3`：核查记录/客观证据；优先通过独立证据工具使用，默认不作为客户口述。
- `S4`：调查员风险推断、结构化结论；只做评估参考，不可生成为客户陈述。
- `S5`：纯生成或扩写信息；V1 不进入真实客户环境。

**Epistemic status（真实性）**：`REPORTED`、`VERIFIED`、`CONTRADICTED`、`UNDETERMINED`。前者回答“来源记录了谁说过什么”，后者回答“内容被什么程度的证据支持”。两者不可互相替代。

### 抽取流程

1. 数据预处理：客户级去重、日期标准化、金额币种/单位、业务来源、PII 脱敏。
2. 原子声明抽取：一个主谓/数值/时间限定尽量单独成为一个 Fact；同句可以对应多个 Fact。
3. Attribution：`CUSTOMER`、`INVESTIGATOR`、`SYSTEM` 或 `UNKNOWN`；归属不明不得自动变成客户陈述。
4. 事实规范化：`attribute`、`value`、`value_qualifier`、实体、语义话题、时间与否定属性。
5. 来源绑定：`source_id`、`span_id`、可审计原文/哈希；多个来源可共享规范化事实但不抹去不同陈述。
6. 冲突/重复处理：不同 source 之间的同义合并保留证据引用；冲突保留两个版本并标注关系。
7. 披露分类：主题级解释 `TOPIC`/`EXPLANATION`，精确信息 `EXACT`，证据 `EVIDENCE`。
8. 时序审计：`valid_at`、`knowledge_available_at`、`cutoff_at`、源记录时间各自独立检查。
9. 质量复核：对 S2 来源归属、带否定词/数字的声明进行规则检查+抽样人工复核。

## Case Package

完整例子见 [`examples/case-package.example.json`](../examples/case-package.example.json)，Schema 见 [`schemas/case-package.schema.json`](../schemas/case-package.schema.json)。

```text
case_id
cutoff_at
public_profile.attributes
hidden_facts[]
source_evidence[]
evaluation_labels[]        # 不暴露给 Risk Agent / Simulator
source_quality_report
split                      # train/val/test（按客户分组）
```

### 关键约束

- `eligible_for_simulator=true` 仅允许 S1/S2 且归属明确为 CUSTOMER，不能仅因文本与风险高度相关就准入。
- 同一客户可以有不同来源说法；事实列表不应为消除冲突而覆盖原文。
- `REPORTED` 不能凭客户重复两次就升级成 `VERIFIED`。
- 如果只存在“客户集中度过高”标签，而没有来源支持具体营收占比，不得虚构比例或金额。
- Gold/Silver/Bronze 是**训练样本实用性分层**而非陈述真实性分层：Gold（QA+可对齐结论/证据）、Silver（明确归属摘要）、Bronze（仅结构化结论）。Bronze 不产生可模拟客户回答。

## Quality gates

- 事实抽取支持率（source-span 对齐率）
- attribution 准确率、数值与否定保真率
- 时间泄漏与跨客户混合率
- 可模拟目标信息覆盖程度（只能估计历史记录覆盖度，不能称为完整真实客户信息覆盖率）
