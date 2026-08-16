# IDEA

## 目标

提供一个可公开复用、可审计的 WorkBuddy + ima 个人 AI 学习 Wiki 模板。

## 当前状态

- 已建立空白 Wiki 目录和项目级 Skill。
- 已提供 ima 增量摄取规范与 WorkBuddy Automation 配置指南。
- 已提供 Skill 打包、项目初始化和发布前验收脚本。
- 不包含任何真实 Wiki、ima 收藏、账号凭据或原项目 Git 历史。
- 已完成发布前本地检查，目标仓库为 `Phil-zy/Learning-Thinking-AI-wiki`。
- 干净克隆验证已通过，仓库所有者已批准创建 `v0.1.0` Release 并公开仓库。

## 决策记录

- WorkBuddy Skill 可作为本地技能包导入。
- WorkBuddy Automation 暂不依赖未公开的导入/导出格式，采用“可复制 Prompt + 手工配置步骤”。
- Automation 仅生成待审核内容，不自动批准合并。
- 增量摄取同时识别全新条目和已更新条目；更新来源保存为新版本，不覆盖 Raw。
- 用户配置与增量状态仅保存在被 Git 忽略的本地文件中。
- 公开发布采用“Private 首次推送 -> 干净克隆验证 -> 用户确认 -> Public”的顺序。
