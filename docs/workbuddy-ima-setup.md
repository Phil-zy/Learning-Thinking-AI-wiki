# WorkBuddy + ima 配置指南

## 1. 准备环境

- 安装 WorkBuddy、Git 和 Python 3.10+。
- 克隆本仓库并在 WorkBuddy 中选择仓库根目录作为工作空间。
- 运行 `scripts/initialize.ps1`。

## 2. 导入 Skill

运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package-skill.ps1
```

在 WorkBuddy 中打开“技能”，选择“上传技能”，上传 `dist/ai-learning-llm-wiki.zip`。导入后确认技能已启用。

如果当前 WorkBuddy 版本支持直接发现项目级 Skill，也可直接保留 `.agents/skills/ai-learning-llm-wiki/`。

## 3. 连接 ima

1. 打开 WorkBuddy 的连接器或资料库管理入口。
2. 选择 ima 并完成账号授权。
3. 只授予完成读取收藏所需的权限。
4. 新建普通任务，请 WorkBuddy 列出可访问的 ima 知识库。
5. 确认目标知识库可见，且能读取一条测试内容。

不同 WorkBuddy 版本的入口与工具名可能变化。本模板要求运行时发现 ima 工具，不把内部 MCP 工具名写死。

## 4. 创建本地配置

```powershell
Copy-Item config/ima-ingest.example.json config/ima-ingest.local.json
```

仅修改本地文件：

- `knowledge_base_name`：目标 ima 知识库的准确名称；
- `topic`：Wiki 主题目录；
- `timezone`：调度时区；
- `max_items_per_run`：单次最大处理量；
- `copyright_mode`：默认保持 `metadata-and-summary`。

不要在该文件中保存密码、Token 或 Cookie。

## 5. 创建 Automation

按 [Automation 配置](../automation/workbuddy-ima-ingest.md)填写名称、工作空间、Skill、连接器、权限、频率和 Prompt。

当前模板不发布 WorkBuddy 内部 `automation-backups/*.json`，也不指导用户直接修改 WorkBuddy SQLite 数据库。这些格式不是公开稳定接口，且可能包含用户归属、内部 ID 和本机路径。

## 6. 审核和合并

Automation 运行后：

1. 阅读 `reviews/<batch>.md`；
2. 查看对应 `staging/` 草稿；
3. 明确批准整批或指定页面；
4. 让 WorkBuddy 按 Skill 的 Approval Merge 执行；
5. 运行 `scripts/verify.ps1`；
6. 自行决定是否提交 Git。

## 7. 最小验收标准

- ima 未连接时不写入 Wiki 文件；
- 首次运行能产生 Raw、Staging 和 Review；
- 重跑不会重复摄取同一 `media_id`；
- 已更新条目产生新的 Raw 版本，不覆盖旧文件；
- 未批准批次不会修改正式 Wiki；
- 批准后索引、日志、证据和工作流门禁全部通过。
