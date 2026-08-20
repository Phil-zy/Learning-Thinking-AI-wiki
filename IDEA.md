# IDEA

## 目标

提供一个可公开复用、可审计、与 Agent 平台和数据来源无关的 AI Knowledge Studio 模板，帮助用户完成外部知识摄取、个人思考沉淀和公开内容准备。

## 当前状态

- 已建立 Raw / Staging / Reviews / Wiki 外部知识管线和完成门禁。
- 已提供 `ai-learning-llm-wiki`，支持网页、文档、用户粘贴和授权连接器来源。
- 已提供 `ai-thinking-writing`，用于想法捕获、澄清、观点确认、内容种子、写作和发布归档。
- 已提供候选笔记、内容种子、Ready 版本和发布前人工检查模板。
- Skill 打包脚本生成两个可独立加载的 ZIP。
- 验证脚本检查两个 Skill、两个门禁、核心与 Adapter 隔离、敏感信息和 Git 差异。
- WorkBuddy + ima 已移动到 `integrations/workbuddy-ima/`，作为可选来源 Adapter。
- 核心初始化不创建 Adapter 配置或状态，不安装任何平台或连接器。
- 公开模板不包含真实知识、个人想法、文章、账号凭据或母库 Git 历史。
- 方案 A 重构已通过核心独立性、Skill 结构、回归测试、打包和隐私检查。
- 本次发布目标为本地和 GitHub `main`，仓库描述使用通用定位。

## 决策记录

- 模板采用“两条输入管线、一个内容输出管线”。
- `ai-learning-llm-wiki` 只负责外部知识；`ai-thinking-writing` 只负责个人观点成熟和内容生产。
- `wiki/` 表示经审核的外部知识；`notes/established/` 表示用户确认的稳定观点。
- 两类知识在 `topics/` 和 `content/seeds/` 汇合。
- 个人想法不能因表达完整而自动升级；候选笔记、稳定观点、内容种子和 Ready 版本都有独立确认门槛。
- `content/ready/` 不授予外部发布权限；平台和最终版本必须再次确认。
- 来源获取具有通用 Interface；网页工具、文件读取、用户粘贴、API 和连接器都是可替换 Adapter。
- 平台专用配置、增量状态、调度和恢复规则只放在 `integrations/<adapter>/`，不进入核心 Skill 包或默认初始化。
- Adapter 获取来源后必须回到 Raw、Staging、Reviews 和用户批准门禁，不能自动合并、提交或推送。
- 两个 Skill ZIP 都包含自身许可证并可独立加载；项目根文档用于增强上下文，不是硬依赖。
- 用户配置和增量状态只保存在 Git 忽略的本地文件中。

## 下一步

1. 在实际修改某个可选 Adapter 时，单独执行该 Adapter 的人工验收。
2. 由用户另行决定是否创建新版本 Release。
