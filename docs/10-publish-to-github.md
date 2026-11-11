# 10 · 发布到新 GitHub 仓库

本项目当前是本地生成的文档与 Schema 项目包；项目包本身**不会自动创建远端仓库**。

## 方案一：使用 GitHub CLI（推荐 Private）

在解压后的项目根目录执行：

```bash
python -m pip install 'jsonschema>=4.20'
python scripts/validate_examples.py

git init
git branch -M main
git add .
git commit -m "docs: initialize risk due diligence agent specification"

gh auth login
gh repo create KotChiu/risk-due-diligence-agent --private --source=. --remote=origin --push
```

若用户不是 `KotChiu` 或已经创建同名仓库，请据实际 owner/repo 改命令；运行前先确认项目不含真实客户信息。

## 方案二：在 GitHub 网页创建空仓库

1. 打开 `https://github.com/new`，仓库名填 `risk-due-diligence-agent`，建议设置为 **Private**。
2. 不要勾选初始化 README（本项目已有 README）。
3. 解压项目并进入根目录，执行：

```bash
git init
git branch -M main
git add .
git commit -m "docs: initialize risk due diligence agent specification"
git remote add origin https://github.com/KotChiu/risk-due-diligence-agent.git
git push -u origin main
```

如新仓库属其他用户名，请替换远程 URL。可使用已有的 Git Credential Manager 或 SSH 设置认证。

## 首次发布检查清单

- [ ] `scripts/validate_examples.py` 全部通过
- [ ] 确认 `examples/` 为虚构样本
- [ ] 没有密钥、生产数据、客户信息、内部业务机密
- [ ] 仓库默认分支与访问权限符合团队要求
- [ ] 将 docs/00 的开放问题保留为待办，不当作既定实验结论
