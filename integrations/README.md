# 可选来源 Adapter

`integrations/` 保存平台或来源专用的接入示例，不属于核心运行依赖。

## Adapter Interface

每个 Adapter 可以负责：

- 发现和访问用户授权的来源；
- 管理自身的本地配置和增量状态；
- 定义分页、去重、更新检测、调度和失败恢复；
- 把取得的来源内容交给 `ai-learning-llm-wiki`。

每个 Adapter 都必须遵守：

- 本地账号、凭据、来源 ID 和状态文件保持 Git 忽略；
- 不绕过 Raw、Staging、Reviews 和用户批准门禁；
- 不自动批准、合并正式 Wiki、提交或推送 Git；
- 核心初始化、Skill 打包和验证在不安装该 Adapter 时仍能运行。

## 当前示例

- [WorkBuddy + ima](workbuddy-ima/README.md)：通过 WorkBuddy Automation 从用户授权的 ima 知识库执行增量摄取。
