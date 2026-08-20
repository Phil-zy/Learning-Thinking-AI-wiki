# 输入、思考与内容输出工作流

## 总体结构

```text
外部资料 → raw → staging → 用户批准 → wiki
                                      ┐
                                       → topics / content seeds → series → drafts → ready → published
                                      ┘
个人表达 → INBOX → 对话澄清 → developing → 用户确认 → established
```

外部知识不等于用户观点，个人体验也不自动成为普遍事实。

## 外部知识管线

由 `ai-learning-llm-wiki` 负责：

```text
来源获取 → Raw → 分类 → Staging → 批次审核 → 用户批准 → Wiki → Lint
```

来源可以由用户粘贴、网页或文件工具、浏览器、API 或授权连接器提供。平台专用的连接器发现、配置、增量状态和调度规则属于 `integrations/` 下的可选 Adapter；取得来源内容后统一进入 Raw、Staging 和审核门禁。外部知识摄取不自动创建个人观点或文章。

## 个人思考管线

由 `ai-thinking-writing` 负责：

```text
原始表达 → inbox/thoughts/INBOX.md → 对话澄清
→ 用户确认值得发展 → notes/developing/
→ 用户确认观点稳定 → notes/established/
```

没有完成澄清和确认的内容继续留在 INBOX 或对话中，不因为表达完整而自动升级。

## 内容输出

内容种子可以引用 `wiki/` 中的外部知识和 `notes/established/` 中的用户观点：

```text
content/seeds/ → content/series/ → content/drafts/
→ 发布前检查 → content/ready/
→ 用户另行授权实际发布 → content/published/
```

`topics/` 只做跨目录导航，不复制正文。`ready/` 表示版本已准备好，不代表已经授权外部发布。

## 常用请求路由

```text
导入网页或文档、摄取外部来源、查询 Wiki、检查 Wiki
→ ai-learning-llm-wiki

记录想法、讨论感受、形成观点、规划文章、准备发布
→ ai-thinking-writing
```

目录在首次产生实际内容时创建；公开模板不预置真实示例内容。
