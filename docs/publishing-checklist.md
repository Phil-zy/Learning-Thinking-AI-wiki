# 公开发布检查清单

## 内容

- [ ] `wiki/`、`raw/`、`reviews/`、`inbox/`、`notes/`、`topics/`、`content/` 中没有真实或私人内容。
- [ ] 示例内容完全虚构或拥有公开授权。
- [ ] 没有真实知识库名称、来源 ID、连接器内部 ID、Automation ID 或时间基准。
- [ ] 没有个人绝对路径、账号、邮箱、Token、Cookie、API Key 或私钥。

## 功能

- [ ] `scripts/initialize.ps1` 可重复运行。
- [ ] `scripts/package-skill.ps1` 能生成两个 Skill ZIP。
- [ ] `scripts/verify.ps1` 全部通过。
- [ ] 两个 Skill 通过结构校验，并能在目标 Agent 环境中加载。
- [ ] 已使用网页、文档或用户粘贴内容人工验证一次外部知识摄取和批准合并。
- [ ] 已人工验证“记录想法”不会自动生成候选笔记或文章。
- [ ] 发布准备门禁不会被误解为外部发布授权。

## 可选 Adapter

- [ ] 不安装任何 `integrations/` Adapter 时，核心初始化、两个 Skill 和验证脚本仍能工作。
- [ ] Adapter 文档明确自身平台、权限、本地配置、状态和停止条件，不把它们写成核心依赖。
- [ ] 若本次修改了某个 Adapter，已完成该 Adapter 自己的人工验收；未修改的 Adapter 不阻塞核心发布。

## GitHub

- [ ] Git 工作区干净。
- [ ] 检查全部提交历史，而不仅是当前文件。
- [ ] 默认分支为 `main`。
- [ ] README、License 和 `.gitignore` 已确认。
- [ ] 仓库可见性明确选择为 Public。
- [ ] 推送前再次检查 `git diff --cached` 和 `git remote -v`。
