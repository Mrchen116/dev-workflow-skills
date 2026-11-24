# Dev Workflow Skills

一套可在项目之间复用、能直接改源码的开发工作流。可从 `dev-workflow` 开始，也可以单独调用需求、设计、调试、审查或产品旅程 skill。

## 安装一次

在需要使用的本地开发环境执行（Python 3.9+ 和 Git）：

```sh
git clone https://github.com/Mrchen116/dev-workflow-skills.git
python3 dev-workflow-skills/install.py
```

默认注册到 Codex 的 `~/.agents/skills/`、Claude Code 的 `~/.claude/skills/` 和 Antigravity 的 `~/.gemini/config/skills/`。只用一个宿主时传 `--target codex`、`--target claude` 或 `--target antigravity`。可以重复执行。同名的其他来源会被列出，安装程序保留它们。使用私有仓库时先登录 GitHub 或使用 SSH clone。Windows 本地安装需要允许创建目录符号链接，WSL 使用其自己的用户目录。

Antigravity App、CLI 和 IDE 共用这个全局目录。在 Antigravity CLI 输入 `/skills` 可以查看已发现的技能。[Google 官方说明](https://antigravity.google/docs/customization-discovery?tab=cli)

## 从任意仓库开始

打开现有业务仓，在新会话里说“用 dev-workflow，先和我对齐导出需求”或“用 change-code-review 看这段 diff”。没有初始化步骤。宿主列出可能使用的技能，实际工作只加载对应流程和资料。项目已有的分支约定、构建命令、产品规范和运行环境仍以项目自己的说明为准。

- [开发生命周期](docs/development/change-workflow.md)
- [专项能力选择](docs/development/skill-composition.md)
- [读取项目约定](docs/development/project.md)

## 在工作中迭代

安装项链接到这份 Git checkout。可以在业务对话里直接说“把这条经验改进通用 skill，提交到 skills 仓库”，并授予宿主对该 checkout 的写权限。提交前在新会话中试用。修改已有 skill 或参考后，同一环境的新会话读取当前文件。新增、移除或改名后重新执行安装，会同步本 checkout 注册的链接。其他环境在独立库运行 `git pull --ff-only` 后重新执行安装即可同步。每个独立容器或远程主机需要自己的 checkout 和注册。

方法和工具相对 skill 的真实目录定位，命令针对当前业务项目运行。项目专属的部署、身份、UI 风格和测试场景应由项目维护。跨平台技能文件可供其他支持 SKILL.md 的宿主集成。
