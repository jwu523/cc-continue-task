# CC Continue Task Skill

[![CI](https://github.com/jwu523/cc-continue-task/actions/workflows/ci.yml/badge.svg)](https://github.com/jwu523/cc-continue-task/actions/workflows/ci.yml)

为长时间 Codex 任务保存和恢复可继续执行的状态，保持目标一致，控制 token 消耗，降低幻觉风险，并避免重复加载项目上下文。 | Save and resume long-running Codex tasks across conversations while preserving the objective, controlling token use, reducing hallucination risk, and avoiding unnecessary project reloads.

[快速开始](#安装) · [使用方式](#使用方式) · [English](README.md)

`cc-continue-task` 是一个 Codex skill，用来给跨多轮对话的大任务保存检查点。它会把可验证的任务状态写入本地 handoff 文件，让新对话可以从明确的状态继续，而不是依赖一整段很长的历史聊天记录。

## 仓库结构

- `SKILL.md`：skill 说明和操作规则。
- `agents/openai.yaml`：Codex agent 元数据。
- `docs/install.md`：详细安装、验证和更新说明。
- `examples/`：脱敏后的示例 handoff，覆盖常见继续任务场景。
- `references/handoff-schema.md`：handoff Markdown 和 JSON 的结构说明。
- `scripts/create_handoff.py`：创建或更新 handoff。
- `scripts/list_handoffs.py`：列出已保存的 handoff。
- `scripts/make_resume_prompt.py`：为新对话生成恢复提示。
- `scripts/sanitize_handoff.py`：扫描 handoff 中的密钥和环境相关信息。
- `scripts/validate_handoff.py`：在恢复或共享前校验 handoff。
- `tests/`：不依赖第三方包的辅助脚本测试。

## 安装

将本仓库 clone 或复制到你的 Codex skills 目录：

```text
<CODEX_HOME>/skills/cc-continue-task
```

如果你的 Codex 环境需要重新加载 skills，请重启 Codex 或执行对应的 reload 操作。

详细安装和验证流程见 [docs/install.md](docs/install.md)。

## 为什么需要它

一些大任务会经历很多轮模型对话。如果一直放在同一个对话里，后期会消耗大量上下文，并增加模型依赖过期信息或产生幻觉的概率。新开对话可以节省上下文，但又容易丢失任务继承关系。

这个 skill 的作用是在两者之间建立一个可控的交接层，只保存继续任务所需的信息：

- 任务目标以及目标来源
- 当前进展和下一步
- 已验证事实、假设、风险和未决问题
- 关键文件、命令和产物
- 上下文加载计划：哪些必须读、哪些按需读、哪些无需重复加载
- 压缩意图：哪些保留、哪些丢弃、哪些恢复时重新验证

## 使用方式

当任务到达一个适合保存的节点时，可以让 Codex 保存 handoff：

```text
Use cc-continue-task to save this task.
Task objective: finish the refactor and verify the CLI still works.
```

如果没有指定目标，skill 应该根据对话内容自动生成一个目标，并在写完 handoff 后主动输出这个目标：

```text
Use cc-continue-task to checkpoint this.
```

在新对话中恢复最近的 handoff：

```text
Use cc-continue-task to resume the latest handoff for this workspace.
```

也可以指定具体 handoff：

```text
Use cc-continue-task to resume .codex/handoffs/my-task/latest.md.
```

保存 handoff 后，也可以先生成一段可直接复制到新对话的恢复提示：

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/my-task
```

## 目标连续性

skill 会同时记录当前 `Objective` 和稳定的 `Original Objective`。

当从 handoff 恢复后再次保存状态时，新 handoff 应该继续围绕原始目标。如果当前对话已经明显偏离原始目标，或者用户手动给出的新目标与原始目标不匹配，skill 应该提示用户调整目标，或建议另存为一个新的 handoff。

这样可以避免一个长期 handoff 在多次保存后悄悄变成另一个任务。

## Handoff 文件

默认情况下，handoff 会写入当前工作空间：

```text
.codex/handoffs/<task-id>/
  latest.md
  handoff.json
  checkpoints/
```

`latest.md` 适合人和后续 Codex 对话阅读。`handoff.json` 是便于工具索引的摘要。`checkpoints/` 用来保存历史 Markdown 快照。

## 脚本示例

创建 handoff：

```powershell
python scripts/create_handoff.py `
  --workspace . `
  --title "Refactor CLI parser" `
  --objective "Finish the CLI parser refactor and verify existing commands still work." `
  --objective-source user_specified `
  --current-state "Parser split is implemented; tests still need to run." `
  --next-step "Run the focused CLI test suite." `
  --must-read "latest.md" `
  --print-path
```

列出 handoff：

```powershell
python scripts/list_handoffs.py --workspace .
```

为新对话生成恢复提示：

```powershell
python scripts/make_resume_prompt.py .codex/handoffs/refactor-cli-parser
```

校验 handoff：

```powershell
python scripts/validate_handoff.py .codex/handoffs/refactor-cli-parser --check-files
```

共享前扫描 handoff：

```powershell
python scripts/sanitize_handoff.py .codex/handoffs/refactor-cli-parser
```

生成脱敏副本：

```powershell
python scripts/sanitize_handoff.py .codex/handoffs/refactor-cli-parser --redact-to redacted-handoffs
```

## 示例

`examples/` 目录包含完全虚构、已脱敏的 handoff 示例：

- `examples/basic/`：用户明确指定目标的普通检查点。
- `examples/generated-objective/`：用户未指定目标，由 Codex 根据对话生成目标。
- `examples/objective-drift/`：恢复后的任务偏离原始目标，应建议另存为新 handoff。

## 质量检查

使用 Python 标准库即可运行本地检查：

```powershell
python -m py_compile scripts/create_handoff.py scripts/list_handoffs.py scripts/make_resume_prompt.py scripts/validate_handoff.py scripts/sanitize_handoff.py
python -m unittest discover -s tests
python scripts/sanitize_handoff.py examples
```

GitHub Actions 会在 push 和 pull request 时运行同样的检查。

## 隐私与脱敏

handoff 文件可能包含本地路径、命令输出、问题细节或运行环境信息。在发布、共享或附加生成的 handoff 前，需要先检查是否包含密钥、账号、内部路径或私有项目内容。

可以先用 `scripts/sanitize_handoff.py` 做第一轮扫描。它会报告疑似凭据、私钥、本地用户路径和私有网络地址，并避免把原始秘密值直接打印出来。

这个仓库只应包含 skill 和辅助脚本。不要提交生成的 `.codex/handoffs/` 数据、本地缓存、凭据、token 或私有项目笔记。

## License

MIT
