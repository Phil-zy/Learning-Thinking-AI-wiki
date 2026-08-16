# AI Wiki Template for WorkBuddy + ima

一个可公开复用的个人 AI 学习 Wiki 模板：使用 WorkBuddy Skill 管理 Markdown 知识库，并通过 WorkBuddy Automation 定期从用户自己的 ima 知识库摄取收藏内容。

## 能做什么

- 从 ima 列出知识库和收藏条目，拉取新增或已更新的内容。
- 将来源保存到 `raw/`，将整理结果先写入 `staging/`。
- 为每批内容生成 `reviews/` 审核报告。
- 只有用户明确批准后，才合并到正式 `wiki/`。
- 自动检查来源证据、链接、索引、批次状态和审计日志。
- 使用 Obsidian 浏览 Markdown Wiki，使用 Git 保存历史。

## 重要限制

WorkBuddy 目前支持导入 Skill，但没有经验证的用户 Automation 导入/导出功能。因此，本仓库提供：

1. 可打包并导入的 `ai-learning-llm-wiki` Skill；
2. 可复制的 Automation Prompt；
3. WorkBuddy 界面配置步骤。

用户需要连接自己的 ima，并创建一次 Automation。仓库不包含任何账号、Token、Cookie、知识库 ID 或 WorkBuddy 内部备份。

## 快速开始

### 1. 克隆并初始化

```powershell
git clone https://github.com/Phil-zy/Learning-Thinking-AI-wiki.git AI-wiki
cd AI-wiki
powershell -ExecutionPolicy Bypass -File scripts/initialize.ps1
```

### 2. 安装 Skill

方式 A：在 WorkBuddy 的“技能”页面选择“上传技能”，上传打包产物：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package-skill.ps1
```

生成文件位于 `dist/ai-learning-llm-wiki.zip`。

方式 B：如果 WorkBuddy 已将当前项目作为工作空间，可直接使用项目级 Skill：

```text
.agents/skills/ai-learning-llm-wiki/SKILL.md
```

### 3. 连接 ima

在 WorkBuddy 中打开连接器管理，连接并授权自己的 ima。具体步骤见 [docs/workbuddy-ima-setup.md](docs/workbuddy-ima-setup.md)。

### 4. 创建本地配置

复制配置样例，填写自己的知识库名称：

```powershell
Copy-Item config/ima-ingest.example.json config/ima-ingest.local.json
```

`config/ima-ingest.local.json` 已被 Git 忽略，不会意外公开。

### 5. 创建 Automation

按 [automation/workbuddy-ima-ingest.md](automation/workbuddy-ima-ingest.md) 配置 WorkBuddy Automation。建议先保持暂停并手动试运行，确认结果后再启用定时执行。

### 6. 验收仓库

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

该命令验证本地静态结构、证据检查、工作流门禁、单元测试和敏感信息规则，不会连接 ima，也不能替代真实的 WorkBuddy/ima 端到端验收。

## 首次试运行

不要直接启用定时执行。先在 WorkBuddy 普通任务中复制 [Automation Prompt](automation/workbuddy-ima-ingest.md)，手动运行一次。

预期结果：

- `raw/<topic>/` 出现来源记录；
- `staging/<topic>/` 出现待审核草稿；
- `reviews/` 出现一个 `Pending approval` 批次报告；
- `.local/ima-ingest-state.json` 仅在整批成功后更新；
- 正式 `wiki/`、`wiki/index.md` 和 `wiki/log.md` 尚未改变。

再次运行时，应跳过相同 `media_id`；远端已更新的条目应生成新的 Raw 版本，而不是覆盖旧文件。

## 审核与合并

1. 阅读 `reviews/<batch>.md`；
2. 检查报告列出的 `staging/` 草稿；
3. 明确批准整批或指定页面；
4. 让 WorkBuddy 使用本 Skill 执行 Approval Merge；
5. 再次运行 `scripts/verify.ps1`；
6. 检查 `git status` 和 `git diff` 后，自行决定是否提交。

完整操作说明见 [WorkBuddy + ima 配置指南](docs/workbuddy-ima-setup.md)。

## 两层验收

- 本地静态验收：`scripts/verify.ps1` 全部通过。
- 端到端人工验收：WorkBuddy 能导入 Skill、ima 授权有效、首次摄取成功、重跑不重复、更新条目生成新版本、批准后合并成功。

公开发布前应从干净克隆重新完成两层验收。

## 工作流

```text
ima 收藏
  -> raw/ 原始证据
  -> staging/ 待审核草稿
  -> reviews/ 批次报告
  -> 用户批准
  -> wiki/ 正式知识
  -> Workflow Gate + Evidence Check
```

Automation 只负责摄取和生成待审核内容，不自动批准、不自动合并正式 Wiki、不自动提交或推送 Git。

## 目录

```text
.agents/skills/ai-learning-llm-wiki/  WorkBuddy Skill、模板、脚本和测试
automation/                           Automation 配置说明和可复制 Prompt
config/                               脱敏配置样例
docs/                                 安装、连接和操作文档
raw/                                  来源证据
staging/                              待审核草稿
reviews/                              批次审核报告
wiki/                                 正式知识页、索引和日志
scripts/                              初始化、打包和验收脚本
```

## 隐私与安全

- 不要提交 `config/*.local.json`、`.workbuddy/`、Token、Cookie、API Key 或个人路径。
- 自动化运行时仅允许访问当前项目目录。
- 对受版权保护的来源只保存必要元数据和合规摘要，除非用户拥有保存原文的权利。
- 首次运行使用低频、最小权限和人工审核。
- 公开推送前运行 `scripts/verify.ps1` 并检查 `git diff --cached`。

## 兼容性

- Windows PowerShell 5.1 或 PowerShell 7
- Python 3.10+
- Git
- WorkBuddy（需支持本地 Skill 导入与 Automation）
- 已授权的 ima 连接器

WorkBuddy 与 ima 的界面、工具名称可能随版本变化。Skill 要求在运行时发现可用连接器工具，不依赖固定 MCP 工具名。

## License

仓库模板采用 MIT License。Skill 目录中保留其原始许可证。
