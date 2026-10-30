# Work with an AI agent

passageway publishes three entry points for an AI agent, all built from this repository.

| Entry point | What it is | Use it when |
|---|---|---|
| [`/SKILL.md`](https://passageway.marceltov.de/SKILL.md) | A general guide for agents: what passageway is, how to install and run it, which route to take for what the human wants. The plugin installs it as the skill `/passageway` | You tell any agent that can fetch a URL: "Read passageway.marceltov.de/SKILL.md and help me set up passageway" |
| The plugin skill [`/create-passageway-connector`](https://passageway.marceltov.de/skills/create-passageway-connector/SKILL.md) | A step-by-step skill for writing, testing and registering a connector | You use Claude Code and want a connector for a new source |
| The plugin skills [`/passageway-connect`](https://passageway.marceltov.de/skills/passageway-connect/SKILL.md) and [`/passageway-add-source`](https://passageway.marceltov.de/skills/passageway-add-source/SKILL.md) | Link Claude Code to a running server (the hook and the MCP server); write a source into `passageway.toml` | You use Claude Code and want it set up without reading the docs yourself |
| [`/llms.txt`](https://passageway.marceltov.de/llms.txt) and [`/llms-full.txt`](https://passageway.marceltov.de/llms-full.txt) | An index of the pages, and the whole documentation as one file | An agent should have all the details in its context |

## Install the plugin in Claude Code

```text
/plugin marketplace add Marceltov/passageway
/plugin install passageway
```

The plugin brings four skills: `/passageway`, the general guide, `/passageway-connect`, `/passageway-add-source` and `/create-passageway-connector`, plus the prompt hook ([Claude Code](claude-code.md)). Every skill names the documentation index and reads the page it needs before acting. Without the plugin, the connector skill is at [`/skills/create-passageway-connector/SKILL.md`](https://passageway.marceltov.de/skills/create-passageway-connector/SKILL.md); an agent can read it from there.

## What the skills do and do not do

- They tell the agent the rules of a connector (stable ids, a version that changes exactly with the content, `list` as the truth for deletions) and how to prove them with the shared contract check.
- They never ask for a secret. Credentials stay in environment variables and `env:NAME` references in `passageway.toml`; the human starts the server and runs the commands that need the password, and the agent reads their output.
- They describe only what exists. The planned features are named as not available.

## Trust and pinning

A skill is a set of instructions that an agent follows, and the file on the site can change with every release. Read it before you hand it to an agent. To use exactly the version of a release, fetch it from that release's tag on GitHub: `https://raw.githubusercontent.com/Marceltov/passageway/v<version>/skills/passageway/SKILL.md`. That works from the first release that includes the skills, which is the one after v0.1.0. The version in the file's header, the plugin and the release tag are checked to be equal when a release is made.

## How the files stay true

The example connector in the skill is the same text as the one in [Write a connector](write-a-connector.md), and a test runs it through the contract check. Other tests check the skill headers, that no skill contains a credential, and that every page of the documentation is in `llms-full.txt`.
