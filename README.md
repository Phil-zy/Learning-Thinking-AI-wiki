# AI Knowledge Studio Template

一个可公开复用、与 Agent 平台和数据来源无关的本地 AI Knowledge Studio：把外部资料沉淀为可追溯 Wiki，把个人经历和想法发展为稳定观点，再将两者组合成经过审核的内容输出。

## 能做什么

- 从网页、论文、课程、文档、用户粘贴文本或授权连接器摄取外部知识。
- 将原始来源保存到 `raw/`，把整理结果先放入 `staging/` 和 `reviews/`。
- 只有用户明确批准后，才将外部知识合并到正式 `wiki/`。
- 自动检查来源证据、链接、索引、批次状态和审计日志。
- 将个人原始想法追加到 INBOX，通过对话逐步发展为候选笔记和稳定观点。
- 连接正式 Wiki 与稳定观点，形成内容种子、系列、草稿和发布准备版本。
- 使用独立发布门禁检查草稿来源、待核实标记、本地路径和疑似凭据。
- 使用 Obsidian 浏览 Markdown，使用 Git 保存修改历史。

## 核心原则

- Agent 是执行者，Skill 是工作流规则，Markdown 文件是长期资产，Git 只负责版本历史。
- 外部知识和用户观点分别维护：`wiki/` 不替代 `notes/established/`。
- 表达完整不代表观点成熟；候选笔记、稳定观点、内容种子和 Ready 版本都有独立确认门槛。
- `content/ready/` 只表示版本准备完成，不授权外部发布。
- 浏览器、文件工具、API 和连接器都是可替换的来源 Adapter，不属于核心运行前提。

## 快速开始

### 1. 克隆并初始化

```powershell
git clone https://github.com/Phil-zy/Learning-Thinking-AI-wiki.git AI-wiki
cd AI-wiki
powershell -ExecutionPolicy Bypass -File scripts/initialize.ps1
```

初始化只准备核心 Wiki 目录和 Git hooks，不安装平台、连接器或可选 Adapter。

### 2. 让 Agent 使用两个 Skill

如果 Agent 能发现项目级 Skill，直接在当前工作区使用：

```text
.agents/skills/ai-learning-llm-wiki/SKILL.md
.agents/skills/ai-thinking-writing/SKILL.md
```

如果 Agent 支持上传 Skill，可以生成两个独立 ZIP：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package-skill.ps1
```

生成文件：

```text
dist/ai-learning-llm-wiki.zip
dist/ai-thinking-writing.zip
```

具体导入方式由所使用的 Agent 平台决定；本仓库不要求某个固定平台。

### 3. 摄取外部资料

可以向具备相应网页或文件访问能力的 Agent 提出：

```text
使用 $ai-learning-llm-wiki 摄取这个网页，先生成 Raw、Staging 和审核报告，不要直接修改正式 Wiki：<URL>
```

也可以提供本地文档或直接粘贴文字。若 Agent 无法访问来源，应由用户提供内容，而不是虚构或绕过访问限制。

### 4. 记录个人想法

```text
记录我刚才关于 AI 使用的这个想法，不要生成文章。
```

素材会追加到 `inbox/thoughts/INBOX.md`。只有经过澄清并得到用户确认后，才会创建 `notes/developing/` 候选笔记。完整流程见 [WORKFLOW.md](WORKFLOW.md)。

### 5. 验收仓库

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

该命令验证核心目录、知识合并门禁、发布准备门禁、两个 Skill 的单元测试、核心与可选 Adapter 的隔离，以及敏感信息规则。它不会替代目标 Agent 环境中的真实来源访问和人工验收。

## 外部知识管线

```text
网页 / 文档 / 粘贴文本 / 授权连接器
  -> raw/ 原始证据
  -> staging/ 待审核草稿
  -> reviews/ 批次报告
  -> 用户批准
  -> wiki/ 正式知识
  -> Workflow Gate + Evidence Check
```

首次试运行应确认：

- `raw/<topic>/` 出现来源记录；
- `staging/<topic>/` 出现待审核草稿；
- `reviews/` 出现 `Pending approval` 批次报告；
- 正式 `wiki/`、`wiki/index.md` 和 `wiki/log.md` 在批准前没有改变。

批准时让 Agent 使用 `ai-learning-llm-wiki` 的 Approval Merge，并再次运行 `scripts/verify.ps1`。

## 个人思考与内容输出

```text
个人表达
  -> inbox/thoughts/INBOX.md
  -> 对话澄清
  -> notes/developing/
  -> 用户确认
  -> notes/established/

wiki/ + notes/established/
  -> content/seeds/
  -> content/series/
  -> content/drafts/
  -> content/ready/
  -> 用户另行授权实际发布
  -> content/published/
```

完整写作约束见 [WRITING_GUIDE.md](WRITING_GUIDE.md)。

## 可选 Adapter

核心仓库不依赖任何 `integrations/` 目录。Adapter 只负责特定平台的来源发现、配置、增量状态、调度和失败恢复；取得来源后仍必须进入同一套 Raw、Staging 和人工审核门禁。

- [Adapter 目录与约束](integrations/README.md)
- [WorkBuddy + ima 增量摄取示例](integrations/workbuddy-ima/README.md)

不使用 WorkBuddy 或 ima 的用户可以完全忽略该示例。

## 目录

```text
.agents/skills/ai-learning-llm-wiki/  外部知识 Skill、模板、脚本和测试
.agents/skills/ai-thinking-writing/   个人思考与内容写作 Skill、模板、脚本和测试
integrations/                          可选的平台或来源 Adapter
docs/                                  发布检查等仓库文档
raw/                                   来源证据
staging/                               待审核草稿
reviews/                               批次审核报告
wiki/                                  正式知识页、索引和日志
inbox/                                 个人原始想法与澄清对话，首次使用时创建
notes/                                 发展中想法与稳定观点，按需创建
topics/                                跨知识和内容的主题导航，按需创建
content/                               内容种子、草稿、Ready 与发布快照，按需创建
scripts/                               初始化、打包和验收脚本
```

## 隐私与安全

- 不要提交 `*.local.json`、Agent 本地状态、Token、Cookie、API Key 或个人路径。
- 将本模板作为公开仓库维护时，不要提交真实 `raw/`、`wiki/`、`inbox/`、`notes/` 或 `content/`；个人使用时应保存在私有仓库。
- Agent 和 Adapter 仅访问用户明确授权的来源及当前工作区。
- 对受版权保护的来源只保存必要元数据和合规摘要，除非用户拥有保存原文的权利。
- 公开推送前运行 `scripts/verify.ps1`，检查全部 Git 历史和 `git diff --cached`。

## 兼容性

- Windows PowerShell 5.1 或 PowerShell 7
- Python 3.10+
- Git
- 能读取和写入当前工作区的 Agent
- 与所选来源相匹配的网页、文件或连接器访问能力

可选 Adapter 可以声明额外的平台或连接器要求，但不能改变核心兼容性。

## License

仓库模板采用 MIT License。两个 Skill 目录中均包含许可证。
