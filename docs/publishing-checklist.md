# 公开发布检查清单

## 内容

- [ ] `wiki/`、`raw/`、`reviews/` 中没有私人内容。
- [ ] 示例内容完全虚构或拥有公开授权。
- [ ] 没有真实知识库名称、ID、`media_id`、Automation ID 或时间基准。
- [ ] 没有个人绝对路径、账号、邮箱、Token、Cookie、API Key 或私钥。

## 功能

- [ ] `scripts/initialize.ps1` 可重复运行。
- [ ] `scripts/package-skill.ps1` 能生成 Skill ZIP。
- [ ] `scripts/verify.ps1` 全部通过。
- [ ] WorkBuddy 能导入生成的 Skill ZIP。
- [ ] 用户已人工验证 ima 连接、首次摄取、增量去重和批准合并。
- [ ] Automation 文档明确说明需要手工创建，未宣称支持导入内部备份。

## GitHub

- [ ] Git 工作区干净。
- [ ] 检查全部提交历史，而不仅是当前文件。
- [ ] 默认分支为 `main`。
- [ ] README、License 和 `.gitignore` 已确认。
- [ ] 仓库可见性明确选择为 Public。
- [ ] 推送前再次检查 `git diff --cached` 和 `git remote -v`。
