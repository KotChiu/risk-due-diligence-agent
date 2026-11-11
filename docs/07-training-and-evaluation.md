# 07 · 训练数据、实验和评估

## 阶段划分

### Phase 0：抽取与模拟器的忠实度基准

从真实历史 QA 建立保留集，并构造等价问法、含错误前提、精确数值、未知细节、时间冲突等测试。检查 Simulator 的 grounded answer、premature disclosure、no-record 和 multi-turn consistency。Simulator 不稳定前，避免大规模 RL。

### Phase 1：Risk Agent SFT

三个任务：

1. Risk Identification：初始/已披露事实 → 风险假设、可见依据、正负信号。
2. Question Planning：公开状态 → 一个针对当前未解决风险的有效问题或 STOP。
3. Risk Updating：旧账本 + 新回答 → 风险增量、置信来源、未决疑点。

使用专家复核的高质量示例与经筛选的历史轨迹。真实历史尽调人员原本问过的问题未必最优，不能原样视作最优策略标签。

### Phase 2：Rollout、离线排序/偏好优化

同案例多路径探索，按证据覆盖、最终风险精准性、成本、状态更新质量筛选。生成 Pairwise Preference 或经过审核的 SFT 轨迹，而非直接拿模拟器任意输出做黄金标签。

### Phase 3：多轮 RL

固定/版本化 Simulator；逐步上线稀疏终局奖励、再叠加经检查的每轮信息增益。监控过度提问、过度风险标记以及环境模型被利用的现象。

## 评估表

| 维度 | 指标 | 注意 |
|---|---|---|
| 风险识别 | Risk Recall / Precision / F1 | 仅可信人工标注或证据明确的标签做主指标 |
| 信息收集 | Evidence/Fact Coverage | 分母是历史可回答目标集，不是全部真实事实 |
| 提问效率 | 新事实/提问、相同预算下覆盖、STOP 质量 | 同义事实去重 |
| 状态更新 | Delta Accuracy、无证据解除率、冲突处理率 | 风险严重度不等于是否已核实 |
| 模拟器质量 | Grounding、数值保真、越权披露、NO_RECORD 处理 | 必须在保留真实 QA 上衡量 |
| 健壮性 | 同意图改写、错误前提、模拟器版本变化 | 减少环境过拟合 |
| 公平性与合规 | 受保护特征/代理变量审计、人审追溯 | 不能直接把敏感属性当负面标签 |

## 对照实验（Ablations）

- 初始画像单轮 Risk Model（0 轮）
- Agent 一次性读取所有**合法可用的历史问答**（历史信息上界的参考，不代表真值上界）
- 规则/随机问题策略 + 相同模拟器
- SFT Agent + 相同轮数预算
- 多轨迹偏好优化 Agent
- RL Agent + 固定/版本化模拟器

同时绘制 0/1/3/5 轮的 Precision、Recall、证据覆盖与成本；不能只画风险发现数量增长。

## 防泄漏分组

- 按真实客户 ID 划分 Train/Val/Test；同客户所有重采样、QA 和轨迹必须在同一 split。
- 如适用再做按时间的 out-of-time 留出集。
- 决策可见性以历史尽调发生时点为基准，future outcome 仅用于离线分析，不可让 Agent 或 Simulator 看见。
- 同一摘要不同切片/表的相似文本做归并，防止近似重复泄漏。
- 每次评估固定 Schema、prompt、model、seed、simulation policy、reward version。

## 报告模板

必须包含样本分组与质量分布、Case Coverage、显式区分真实/合成来源、每轮和终局指标、置信区间/错误分组、典型轨迹 Badcase、环境故障率，以及失败案例证据链接。
