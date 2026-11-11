# 09 · MVP 里程碑与验收

## Milestone 1 · Case Package Builder

交付：数据解析 → S1–S5 分级、归属、时间、来源引用、冲突检测；`case-package.schema.json` 与样例。

验收：随机抽样可追踪每个 Fact 的原始 span；数值、否定与客户/调查员归属审查通过；S4/S5 不进入 Simulator 可答集合；客户级分组无跨 split 泄漏。

## Milestone 2 · Grounded Customer Simulator

交付：Question Parser、混合检索、DisclosurePlan、受限生成器、Grounding Verifier、安全回退。

验收：典型问题可回答；对无证据数值、带错误前提、越权披露和未记载信息均有可靠行为；真实 QA 留出集指标报告完整。

## Milestone 3 · Risk Agent + Episode Runner

交付：三任务 Agent、ASK/STOP、Risk Ledger、Event Store、reset/step/trace、端到端四轮演示。

验收：风险增量可回放，重复事实不重复奖励，私有 audit 与 eval labels 不进入 Agent 观察，预算耗尽与异常截断可区分。

## Milestone 4 · SFT 与基准

交付：风险识别/问题规划/风险更新 SFT 数据集，零轮/规则策略/多轮 SFT 的并行评估。

验收：在独立客户级留出集提供 Precision、Recall、Fact Coverage、Update Accuracy、问答成本、模拟器错误率与 Badcase。

## Milestone 5 · Rollout + RL（在前四阶段可靠后）

交付：同 Case 多轨迹、多 Seed 评测、奖励防作弊、偏好优化与多轮 RL 实验。

验收：相同轮数预算下与 SFT baseline 比较，并检查 Recall 提升是否由 Precision 下降或 Simulator 泄漏换得。

## 最小本地执行建议

1. 使用 `examples/` 中的虚构 C001 先跑静态规则 Simulator（不调用 LLM），验证信息权限、状态与事件顺序。
2. 替换成受约束 LLM 生成器，并跑模拟器 Fidelity Bench。
3. 接上任意基座模型的三任务 Prompt，先录制真实可复现的 Episode。
4. 才考虑微调或 RL；避免同时改数据层、Simulator 和奖励导致无法定位问题。

## 推荐工程接口

```python
class CaseRepository:
    def load(self, case_id: str): ...

class CustomerSimulator:
    def answer(self, question: str, case_state, disclosure_history): ...

class RiskAgent:
    def act(self, public_observation): ...
    def update(self, public_observation, answer): ...

class EpisodeEnvironment:
    def reset(self, case_id: str, seed: int): ...
    def step(self, action): ...

class Verifier:
    def score(self, private_trace): ...
```

这组类定义用于指导后续实现，不代表已有功能或具体训练框架绑定。
