# AI Wiki Template：项目规则

本仓库是可公开复用的 WorkBuddy + ima 个人 LLM Wiki 模板。

## 工作流入口

项目级 `.agents/skills/ai-learning-llm-wiki/SKILL.md` 是 Wiki 结构、摄取、审核、合并、查询、归档与 Lint 的唯一规范。执行相关任务前必须完整读取该 Skill，并按需读取它直接引用的 `references/`。

## 公开模板边界

- 不写入或提交真实账号、Token、Cookie、API Key、知识库 ID、连接器内部 ID、Automation ID 或个人绝对路径。
- 用户本地配置只写入 `config/ima-ingest.local.json`；该文件必须保持忽略。
- `.workbuddy/` 是本地运行状态，不纳入版本控制。
- 示例内容必须是虚构或明确授权公开的内容。
- WorkBuddy Automation 只摄取到 `raw/`、`staging/`、`reviews/`；未经用户明确批准，不写入正式 `wiki/`。
- 不依赖 WorkBuddy 内部 Automation JSON 或 SQLite 数据库；这些不是公开稳定接口。

## Git

- 未经用户明确要求，不添加远程、不推送、不改写历史。
- 写入任务结束前运行 `scripts/verify.ps1`、`git status` 和 `git diff --check`。
- 报告新增、修改、移动和删除的文件；没有删除也要说明。

## 语言

文档、Wiki 草稿和审核报告默认使用中文；首次出现的重要英文术语保留原文。
