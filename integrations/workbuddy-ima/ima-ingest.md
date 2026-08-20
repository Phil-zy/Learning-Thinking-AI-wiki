# ima 增量摄取规则

仅当用户明确选择 WorkBuddy + ima 作为来源访问方式时读取本 Adapter。它只扩展来源获取，不改变核心摄取工作流。

## 前置条件

1. 从项目根目录读取 `integrations/workbuddy-ima/config.local.json`。
2. 配置缺失、JSON 无效或仍包含占位值时停止。
3. 在运行时发现可用的 ima 连接器工具，不依赖固定 MCP 服务或工具名称。
4. 必须具备等价能力：
   - 列出可访问知识库；
   - 列出指定知识库中的条目；
   - 获取单条内容及其元数据。
5. `knowledge_base_name` 必须唯一匹配一个可访问知识库；同名时不得猜测。
6. 不把连接器凭据、账号标识、OAuth Token、Cookie 或知识库内部 ID 写入仓库。

## 本地状态

使用 `.local/ima-ingest-state.json`。整个 `.local/` 目录只供本地使用并由 Git 忽略。

推荐结构：

```json
{
  "schema": 1,
  "knowledge_base_name": "user supplied name",
  "last_successful_run": "ISO-8601 timestamp",
  "max_create_time": 0,
  "items": {
    "opaque-media-id": {
      "create_time": 0,
      "remote_version": "optional opaque value",
      "last_seen_update_marker": "optional text",
      "raw_versions": ["raw/topic/file.md"]
    }
  }
}
```

不得把示例占位值写入真实批次报告。

## 候选项选择

同时使用两个维度：

1. **全新条目**：状态中不存在主标识；有 `media_id` 时优先使用。`create_time > max_create_time` 只能作为快速路径，不能作为唯一判断。
2. **已更新条目**：标识已存在，但远端版本或更新字段发生变化，或者远端文字包含配置的更新标记。

不要只依赖 `create_time`；部分系统编辑后仍保留原始创建时间。

缺少稳定标识时，从连接器提供的不可变标识中保守派生。存在同名条目时不能只用标题去重。

## 获取与版权处理

- 每次最多获取 `max_items_per_run` 个候选项。
- 默认 `copyright_mode` 为 `metadata-and-summary`：保存规范 Raw 元数据、必要主张摘要、允许保存的稳定不透明来源标识和来源限制。除非用户提供原文或明确拥有保存全文的权利，不保存整篇受版权保护文章。
- 每个 Raw 文件必须使用 `.agents/skills/ai-learning-llm-wiki/references/raw-template.md` 定义的 `Source`、`Collected` 和 `Published` 字段。
- 不覆盖 Raw。来源更新时使用 `-v2`、`-v3` 等新文件名。

## 分类与审核

- 全新候选通常分类为 New，但决定前仍要搜索 `wiki/` 和 `staging/`。
- 已更新候选与既有 Raw、Wiki 比较后，分类为 Update、No material 和/或 Disputed。
- 在批次报告中写明更新差异摘要。
- 每次运行创建唯一批次报告。
- 停止在 `Pending approval`。Automation 不得批准自己的输出。

## 状态提交规则

把本地状态视为提交标记：

1. 获取候选项。
2. 写入全部 Raw、Staging 草稿和批次报告。
3. 运行证据检查和适用的 premerge 检查。
4. 只有全部必要产物成功后，才原子替换 `.local/ima-ingest-state.json`。

失败时保留旧状态，使下次可以安全重试。报告部分产物，不得把失败候选标记为已消费。

## 完成报告

报告：

- 可访问知识库和目标匹配结果；
- 检查的远端条目总数；
- 选中的全新和已更新候选；
- New、Update、No material 和 Disputed 数量；
- 获取失败项及重试安全性；
- 创建的 Raw、Staging 和 Review 文件；
- 等待用户批准的准确项目。

无人值守的摄取 Automation 不得执行 Approval Merge、删除 Staging 草稿、提交 Git 或推送远端。
