---
name: dev-workflow
description: 用户要求按开发体系推进需求、修复、设计、实施、审查或复盘时，选择合适的流程。可在任意 Git 项目中使用。
---

# 开发工作流

以当前工作目录所在的业务仓库为工作对象。先看任务、用户指定的停止位置和已有项目说明，必要时从仓库脚本、测试或 CI 确认项目用法。只有本次需要记录正式变更时才建立 unit。

- 只要讨论、调查或审查时，做到用户指定的阶段。已观察到故障可读 [systematic-debugging](../systematic-debugging/SKILL.md)，单独审查 diff 可读 [change-code-review](../change-code-review/SKILL.md)。
- 无需对齐的小修直接改并做最窄验证。小修完成后用 `git diff --check` 核对补丁。正式变更按[变更流程](../../docs/development/change-workflow.md)选择 Full 或 Bugfix lite，从 [change-spec-author](../change-spec-author/SKILL.md) 开始。已对齐的 unit 从已有阶段恢复。用户明确选快速开发时沿用该路径。
- 专项能力按[本次需要回答的问题](../../docs/development/skill-composition.md)选择。用户点名某个 skill 时可直接调用它。
- 业务改动和验收证据写进业务仓。用户要求改进开发方法时，解析已加载 skill 的真实路径，在该独立 Git checkout 修改、验证、提交；推送使用独立库自己的 remote。
