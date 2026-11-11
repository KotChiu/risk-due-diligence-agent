# Risk Due Diligence Agent

> 基于真实尽调证据的多轮风险发现 Agent：形成风险假设 → 主动提问 → 获得客户解释 → 更新风险账本 → 决定追问或停止。

**项目阶段：设计文档与数据协议 V1.0（尚未实现模型服务或进行训练）。** 本仓库是经过讨论确认的设计基线，不应被解读为已经验证的实验结论。

## 已确认的产品决策

- **目标 A：风险发现与尽调**，不直接输出授信额度或自动作出贷款审批决定。
- **客户侧先使用模拟 Agent**，训练期通过真实历史 QA、尽调摘要与结构化结论构建训练环境。
- **混合证据模式**：仅真实客户陈述与明确归属的摘要陈述可进入可对话知识；调查核验事实走独立证据渠道；主观风险结论只供评估。
- **语义相关披露**：宽泛问题允许简短解释及直接背景信息；精确金额/比例/时间原则上需具体追问。
- **结构化 Risk Ledger + 事件日志**，每轮记录新事实、来源、披露及风险状态变化。
- **第一版动作 `ASK` / `STOP`**，默认每轮一个问题；先建立模拟器、SFT 基线，后进行多轨迹比较及 RL。

其他细节（例如每回合最多披露事实数量、训练轮数、奖励系数）仍是 V1 工程默认值，**不是已经确认的最终超参**。详见 [决策记录](docs/00-decisions-and-assumptions.md)。

## 仓库结构

```text
risk-due-diligence-agent/
├── README.md
├── docs/
│   ├── 00-decisions-and-assumptions.md
│   ├── 01-system-architecture.md
│   ├── 02-evidence-and-case-builder.md
│   ├── 03-customer-simulator.md
│   ├── 04-risk-agent-and-state.md
│   ├── 05-runtime-and-api.md
│   ├── 06-rl-environment-and-reward.md
│   ├── 07-training-and-evaluation.md
│   ├── 08-security-and-governance.md
│   ├── 09-implementation-roadmap.md
│   └── 10-publish-to-github.md
├── schemas/
│   ├── fact.schema.json
│   ├── case-package.schema.json
│   ├── question-intent.schema.json
│   ├── disclosure-plan.schema.json
│   ├── agent-action.schema.json
│   ├── risk-ledger.schema.json
│   ├── simulator-audit.schema.json
│   └── episode.schema.json
├── examples/
│   ├── case-package.example.json
│   ├── question-intent.example.json
│   ├── disclosure-plan.example.json
│   ├── risk-ledger.example.json
│   └── episode.example.json
└── scripts/
    └── validate_examples.py
```

## 快速检验

环境要求：Python 3.10+；仅验证脚本依赖 [`jsonschema`](https://pypi.org/project/jsonschema/) 与 `referencing`（通常为 jsonschema 的依赖）。

```bash
python -m pip install 'jsonschema>=4.20'
python scripts/validate_examples.py
```

验证内容：全部 Schema 可解析、示例满足 Schema、Case Package 中 S1/S2 披露范围、Episode 已披露 Fact 引用与重复披露处理等基础语义约束。它**不等同于模型回答真实性评测**。

## 阅读导航

| 文档 | 核心问题 |
|---|---|
| [01 架构](docs/01-system-architecture.md) | 哪些组件运行、看什么信息、谁能计算 Reward |
| [02 证据库](docs/02-evidence-and-case-builder.md) | 历史 QA / 摘要 / 结论如何加工成事实 |
| [03 模拟客户](docs/03-customer-simulator.md) | 如何识别问题、匹配事实、受约束披露与生成回答 |
| [04 风险与状态](docs/04-risk-agent-and-state.md) | 风险生命周期、事件更新、冲突处理 |
| [05 协议](docs/05-runtime-and-api.md) | reset/step/trace 的请求和可见性边界 |
| [06 RL](docs/06-rl-environment-and-reward.md) | POMDP、动作、奖励、缺失记录与终局评估 |
| [07 训练评估](docs/07-training-and-evaluation.md) | 数据划分、SFT、Rollout、RL、对照实验 |
| [08 安全合规](docs/08-security-and-governance.md) | 客户隐私、审计与授信公平性 |
| [09 路线图](docs/09-implementation-roadmap.md) | MVP 阶段交付物与验收标准 |
| [10 GitHub 协作](docs/10-publish-to-github.md) | 已发布仓库的克隆、验证与协作方式 |

## 端到端示例

`examples/case-package.example.json` 是**虚构脱敏示例**：初始画像显示经营流水下降 35%；历史陈述包括更换大客户、结算周期延长、最大客户约占营收 60%、约 100 万应收款、预计下月回款。`examples/episode.example.json` 展示四轮 ASK + STOP，模拟回答如何逐步披露，Risk Agent 如何更新风险状态。数值纯属示意。

## 贡献约定

- 新增事实字段必须保留来源和原文跨度（provenance）；客户陈述≠经过核实的事实。
- 禁止把评估标签或贷后结果引入 Agent 的公开 Observation 或 Simulator 的回答生成上下文。
- Schema 修改必须同步更新示例与 `scripts/validate_examples.py`。
- 未有证据支持时，应输出未知/待核实，不能虚构合同、回款、客户信息。
- 当前仅供研究/辅助尽调；若用于实际信贷流程，须经数据治理、模型风险和合规审核。

## 许可证与仓库可见性

未预设开源许可证；**当前仓库为 Public**。仅允许提交虚构示例与可公开的设计资料；不得提交真实客户资料、未公开业务规则或内部凭据。接入生产数据前须确认组织授权、数据合规与仓库可见性。
