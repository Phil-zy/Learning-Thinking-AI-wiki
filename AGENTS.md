# AI Knowledge Studio Template：项目规则

本仓库是可公开复用的 WorkBuddy + ima AI Knowledge Studio 模板。它提供外部知识摄取、个人思考沉淀和内容发布准备三段式工作流，但不包含任何真实知识、私人想法或账号配置。

## 工作流入口

- `.agents/skills/ai-learning-llm-wiki/SKILL.md`：外部知识管线，负责 ima/网页/文档摄取、Raw、Staging、审核、Wiki、Query、Lint 和完成门禁。
- `.agents/skills/ai-thinking-writing/SKILL.md`：个人思考与内容管线，负责想法捕获、对话澄清、观点确认、内容种子、写作、发布准备和发布归档。

`PROJECT.md` 说明统一定位，`WORKFLOW.md` 说明两条管线如何汇合，`WRITING_GUIDE.md` 约束公开写作。处理任务前读取当前任务对应的 Skill；跨管线任务同时遵守两者，不得用其中一条绕过另一条的确认门槛。

## 规则优先级

1. 用户当前任务中的明确指令。
2. 本文件的模板安全与共享规则。
3. 当前任务对应的项目级 Skill。
4. Skill 明确引用的项目文档和模板。
5. 其他 Agent 默认行为。

## 公开模板边界

- 不写入或提交真实账号、Token、Cookie、API Key、知识库 ID、连接器内部 ID、Automation ID、联系方式、个人绝对路径或未授权对话。
- 不提交真实 `raw/`、`wiki/`、`reviews/`、`inbox/`、`notes/`、`topics/` 或 `content/` 数据；模板目录只保留初始化文件或明确虚构的示例。
- 用户本地配置只写入 `config/ima-ingest.local.json`；该文件必须保持忽略。
- `.workbuddy/` 与 `.local/` 是本地运行状态，不纳入版本控制。
- 示例内容必须完全虚构或明确授权公开，不能从母库复制真实知识或个人素材。
- WorkBuddy Automation 只摄取到 `raw/`、`staging/`、`reviews/`；未经用户批准，不写入正式 `wiki/`。
- 不依赖 WorkBuddy 内部 Automation JSON 或 SQLite 数据库；这些不是公开稳定接口。

## 来源、观点与发布权限

- 用户是自身经历、感受、观点、立场和表达意图的唯一来源。不得虚构，也不得把 Agent 建议包装为用户观点。
- 始终区分外部事实、用户经历、用户感受、当前解释、推测假设、稳定观点、公开主张和 Agent 建议。
- `wiki/` 表示经审核的外部知识；`notes/established/` 表示用户确认的稳定观点。不要互相替代。
- “记录想法”不授权生成候选笔记或文章；成熟度升级依照 `ai-thinking-writing`。
- `content/ready/` 表示指定版本通过发布前准备，不授权实际发布。
- 向微信公众号、网站或其他平台发送内容，必须再次确认平台和最终版本。
- 不自动提交、不自动推送，也不自动发布内容。

## 隐私与版权

- 对受版权保护的外部来源只保存必要元数据、合规摘录和摘要，除非用户拥有保存原文的权利。
- 将敏感资料发送给在线模型或第三方服务前必须取得明确同意。
- 公开内容不得包含密钥、账号、个人路径、私有仓库、未授权对话或可识别个人及第三方的信息。

## Git 与验收

- 未经用户明确要求，不添加远程、不推送、不改写历史。
- 写入任务结束前运行 `scripts/verify.ps1`、`git status` 和 `git diff --check`。
- 公开发布前执行 `docs/publishing-checklist.md`，并确认全部 Git 历史不包含私人数据，而不只是检查当前文件。
- 报告新增、修改、移动和删除的文件；没有删除也要说明。

## 语言

文档、Wiki、个人笔记、内容草稿和审核报告默认使用中文；首次出现的重要英文术语保留原文。
