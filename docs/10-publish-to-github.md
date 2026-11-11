# 10 · GitHub 仓库与协作指南

> 本项目已于 2026-11-11 发布到 [KotChiu/risk-due-diligence-agent](https://github.com/KotChiu/risk-due-diligence-agent) 的 `main` 分支。本文件记录后续克隆、验证、修改和重新发布的办法。

## 开始使用

```bash
git clone https://github.com/KotChiu/risk-due-diligence-agent.git
cd risk-due-diligence-agent
python -m pip install 'jsonschema>=4.20'
python scripts/validate_examples.py
```

当前是**方案设计与数据协议**项目，还没有完成运行中的模型服务、Simulator 或 RL 训练器。

## 修改与发布

建议通过独立 feature 分支提交 Schema、文档和示例修改：

```bash
git checkout -b feature/<short-description>
# 编辑文档、Schema、示例
python scripts/validate_examples.py
git add docs schemas examples scripts README.md
git commit -m "docs: update agent specification"
git push -u origin HEAD
```

然后在 GitHub 上创建 Pull Request 进行评审。Schema 发生变更时，必须同步更新示例与验证脚本。

## 仓库可见性与数据

首次发布时仓库为 **Public**。此仓库的样例均为虚构数据；请勿提交真实客户画像、客户身份信息、未脱敏历史 QA、内部凭据或生产环境密钥。涉及真实尽调数据时，应迁移到符合组织数据安全要求的私有环境，并做好脱敏、权限隔离与审计。

## 重新发布到其他仓库

如需迁移，请在目标 GitHub 仓库创建空仓库，再将 `origin` 修改为目标地址并推送。不要对已经存在文件的远端分支强制推送。

详细的已确认架构、数据范围和未决工程假设请参阅 [决策记录](00-decisions-and-assumptions.md)。
