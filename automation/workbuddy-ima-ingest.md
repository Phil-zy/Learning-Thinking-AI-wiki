# WorkBuddy Automation：ima 增量摄取

## 当前兼容边界

WorkBuddy 支持本地保存 Automation 和使用内置任务模板，但尚未验证用户自建 Automation 的公开导入/导出格式。本文件不是内部备份，不能直接导入 Automation；它提供可复制配置和 Prompt。

## 创建前检查

1. 将本仓库作为 WorkBuddy 工作空间。
2. 导入或启用 `ai-learning-llm-wiki` Skill。
3. 在连接器管理中连接并授权自己的 ima。
4. 复制 `config/ima-ingest.example.json` 为 `config/ima-ingest.local.json`，填写知识库名称。
5. 确认 `config/ima-ingest.local.json` 仍被 Git 忽略。

## 推荐 Automation 配置

| 配置项 | 推荐值 |
|---|---|
| 名称 | ima 增量摄取到 AI Wiki |
| 工作空间 | 当前仓库根目录 |
| Skill | ai-learning-llm-wiki |
| 连接器 | 用户已授权的 ima 连接器 |
| 权限 | 最小可用权限；只允许当前仓库 |
| 频率 | 首次手动运行；稳定后每周一次 |
| 通知 | 运行失败和出现待审核批次时通知 |
| 初始状态 | 暂停，试运行通过后启用 |

## 可复制 Prompt

将以下内容作为 Automation 的完整 Prompt：

```text
使用 $ai-learning-llm-wiki 执行一次 ima 增量摄取。

开始前：
1. 将当前工作空间视为项目根目录，完整读取 AGENTS.md、Skill 的 SKILL.md，以及 Skill 直接引用的 ima-ingest.md。
2. 读取 config/ima-ingest.local.json。若文件不存在、JSON 无效或 knowledge_base_name 仍是占位符，停止并报告；不要写入任何 Wiki 文件。
3. 在当前已授权连接器中发现 ima 能力，不依赖固定 MCP 工具名。必须能完成：列出知识库、列出条目、获取单条内容。若任一能力不可用，停止并报告；不要写入任何 Wiki 文件。
4. 仅访问配置指定的知识库。若同名知识库不是唯一匹配，停止并请用户选择。

摄取时：
1. 列出知识库全部条目，并读取 .local/ima-ingest-state.json；状态不存在时，从 raw/ 中的可选 ima 元数据重建去重集合。
2. 用 media_id 作为主去重键。全新条目进入 New 流程；已有 media_id 但远端显示更新标记或版本字段变化的条目，重新拉取并进入 Update/No material triage。
3. 不覆盖任何既有 raw 文件。更新版本使用新的文件名后缀，例如 -v2、-v3。
4. 根据版权模式保存来源：默认仅保存来源元数据、必要主张摘要与来源限制；除非用户明确有权保存全文，否则不要复制整篇受版权保护内容。
5. 严格执行 Skill 的 triage、compile、cascade 和 batch review 流程。正式 wiki/、wiki/index.md 和 wiki/log.md 在用户批准前不得修改。
6. 每批最多处理 max_items_per_run 条；超出的保留到下次运行。
7. 只有 Raw、草稿和批次报告全部成功落盘后，才原子更新 .local/ima-ingest-state.json。失败时保留旧状态，并在报告中说明可安全重试。

结束时：
1. 运行证据检查和适用的 premerge 工作流检查。
2. 报告拉取总数、New/Update/No material/Disputed 数量、失败项、生成文件和待用户批准项。
3. 不自动批准、不自动合并正式 Wiki、不删除 staging 草稿、不执行 git commit 或 git push。
```

## 首次试运行

1. 保持 Automation 暂停。
2. 在普通任务中复制同一 Prompt 手动运行。
3. 确认只新增 `raw/`、`staging/`、`reviews/` 和 `.local/`。
4. 检查报告中的来源、版权模式、待核实项和草稿。
5. 用户明确批准后，单独执行 Approval Merge。
6. 运行 `scripts/verify.ps1`。
7. 确认无误后再启用定时执行。

## 失败恢复

- ima 未连接：重新授权后重跑；不应产生半批次。
- 同名知识库：修改本地配置，使名称唯一；不要猜测。
- 单条内容拉取失败：在批次报告中记录失败项，不推进该条目的状态。
- 运行中断：旧增量状态保持不变；下一次应安全重试。
- 已更新条目：创建 Raw 新版本并等待审核，不覆盖历史来源或正式 Wiki。
