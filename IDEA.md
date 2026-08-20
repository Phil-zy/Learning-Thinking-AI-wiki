# IDEA

## 目标

提供一个可公开复用、可审计的 WorkBuddy + ima AI Knowledge Studio 模板，帮助用户完成外部知识摄取、个人思考沉淀和公开内容准备。

## 当前状态

- 已建立空白 Raw / Staging / Reviews / Wiki 结构和外部知识完成门禁。
- 已提供 ima 增量摄取规范、脱敏配置样例和 WorkBuddy Automation 配置指南。
- 已提供第二个项目级 `ai-thinking-writing` Skill，用于想法捕获、澄清、观点确认、内容种子、写作和发布归档。
- 已提供候选笔记、内容种子、Ready 版本和发布前人工检查模板。
- 已增加本地发布准备门禁及 5 个回归测试；外部知识门禁保留原有 13 个测试。
- Skill 打包脚本现在同时生成 `ai-learning-llm-wiki.zip` 和 `ai-thinking-writing.zip`。
- 验收脚本同时检查两个 Skill、两个门禁、敏感信息和 Git 差异。
- 不包含任何真实 Wiki、ima 收藏、个人想法、文章、账号凭据或母库 Git 历史。
- 本次升级已完成差异审核和阻断问题修复，提交目标为 `codex/upgrade-knowledge-studio-template` 分支。

## 决策记录

- 模板采用“一个私有使用 Vault、两条输入管线、一个内容输出管线”。
- `ai-learning-llm-wiki` 只负责外部知识；`ai-thinking-writing` 只负责个人观点成熟和内容生产。
- `wiki/` 表示经审核的外部知识；`notes/established/` 表示用户确认的稳定观点。
- 两类知识在 `topics/` 和 `content/seeds/` 汇合。
- 个人想法不能因表达完整而自动升级；候选笔记、稳定观点、内容种子和 Ready 版本都有独立确认门槛。
- `content/ready/` 不授予外部发布权限；平台和最终版本必须再次确认。
- WorkBuddy Automation 只生成 Raw、Staging 和 Reviews，不自动批准或合并。
- WorkBuddy Skill 可以打包导入；Automation 仍采用可复制 Prompt 和人工配置，不依赖未公开的内部备份格式。
- 两个 Skill ZIP 都应包含自身许可证并可独立加载；项目根文档用于增强上下文，不作为独立 Skill 的硬依赖。
- 用户配置与增量状态只保存在 Git 忽略的本地文件中。
- 公开模板只保留空目录、规范、脚本和虚构示例，不复制母库真实数据。
- 公开发布继续采用“Private 首次推送 → 干净克隆验证 → 用户确认 → Public”的顺序。

## 下一步

1. 审核 GitHub 分支差异并决定是否合并到 `main`。
2. 人工验证 WorkBuddy 导入两个 Skill ZIP 后，再决定是否创建新版本 Release。
