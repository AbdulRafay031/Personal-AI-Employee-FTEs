# Personal AI Employee FTEs - Project Context

## Project Overview

This repository contains a **hackathon blueprint** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI agent that manages personal and business affairs 24/7. The project uses **Claude Code** as the reasoning engine and **Obsidian** as the local-first dashboard/memory system.

**Core Philosophy:** Local-first, agent-driven, human-in-the-loop automation. The AI proactively manages tasks rather than waiting for user input.

**Key Innovation:** The "Monday Morning CEO Briefing" — where the AI autonomously audits bank transactions and tasks to report revenue and bottlenecks, transforming from a chatbot into a proactive business partner.

## Architecture

### The 4-Layer Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian (Markdown) | Local dashboard, knowledge base, state management |
| **Senses** | Python Watcher Scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI |
| **Hands** | MCP Servers | Model Context Protocol for external actions (email, browser, payments) |

### Perception → Reasoning → Action Flow

1. **Perception (Watchers):** Lightweight Python scripts monitor inputs and create `.md` files in `/Needs_Action`
2. **Reasoning (Claude):** Reads tasks, creates `Plan.md` with checkboxes, determines next actions
3. **Action (MCP):** Executes via MCP servers (email, browser automation, payments) with human-in-the-loop approval

## Directory Structure

```
Personal-AI-Employee-FTEs/
├── .qwen/skills/                    # Qwen agent skills
│   └── browsing-with-playwright/    # Browser automation skill
│       ├── SKILL.md                 # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py        # MCP client for tool calls
│           ├── start-server.sh      # Start Playwright MCP server
│           ├── stop-server.sh       # Stop Playwright MCP server
│           └── verify.py            # Server health check
├── skills-lock.json                 # Skills version tracking
├── .gitattributes                   # LF line ending normalization
└── QWEN.md                          # This file
```

### Expected Obsidian Vault Structure (Created by User)

```
AI_Employee_Vault/
├── Dashboard.md                     # Real-time status summary
├── Company_Handbook.md              # Rules of engagement
├── Business_Goals.md                # Q1/Q2 objectives, metrics
├── Inbox/                           # Raw incoming items
├── Needs_Action/                    # Pending tasks (Watcher output)
├── In_Progress/<agent>/             # Claimed tasks (claim-by-move rule)
├── Pending_Approval/                # HITL approval requests
├── Approved/                        # Approved actions ready for execution
├── Rejected/                        # Rejected actions
├── Done/                            # Completed tasks
├── Plans/                           # Generated plan files
├── Accounting/
│   └── Current_Month.md             # Transaction logs
└── Briefings/
    └── YYYY-MM-DD_Monday_Briefing.md # CEO briefings
```

## Key Concepts

### Watchers
Lightweight Python scripts that continuously monitor:
- **Gmail:** Unread/important emails → `/Needs_Action/EMAIL_<id>.md`
- **WhatsApp:** Keyword-triggered messages (urgent, invoice, payment) → `/Needs_Action/`
- **Filesystem:** Drop folder monitoring → `/Needs_Action/FILE_<name>.md`
- **Finance:** Bank transaction CSV/API polling → `/Accounting/Current_Month.md`

### Ralph Wiggum Loop (Persistence Pattern)
A Stop hook that intercepts Claude's exit and re-injects the prompt until the task is complete:
- Orchestrator creates state file with prompt
- Claude works on task
- Stop hook checks: Is task file in `/Done`?
- If NO → Block exit, re-inject prompt (loop continues)
- If YES → Allow exit (task complete)

### Human-in-the-Loop (HITL)
For sensitive actions (payments, sending emails):
1. Claude creates `APPROVAL_REQUIRED_<action>.md` in `/Pending_Approval/`
2. User reviews and moves file to `/Approved/` or `/Rejected/`
3. Orchestrator triggers MCP action only for approved items

### Claim-by-Move Rule (Multi-Agent Coordination)
- First agent to move a task from `/Needs_Action/` to `/In_Progress/<agent>/` owns it
- Other agents must ignore claimed tasks
- Prevents duplicate work

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts, orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control for vault |

**Hardware:** Minimum 8GB RAM, 4-core CPU, 20GB free disk. Recommended: 16GB RAM, 8-core CPU, SSD.

### Starting the Playwright MCP Server

```bash
# Start (recommended - uses helper script)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Or manually
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

**Important:** The `--shared-browser-context` flag is required to maintain browser state across multiple calls.

### MCP Server Configuration

Configure in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

### Recommended MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in, use for vault |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |
| `calendar-mcp` | Create, update events | Scheduling |
| `slack-mcp` | Send messages, read channels | Team communication |

## Development Conventions

### File Naming Conventions

- **Action Files:** `EMAIL_<id>.md`, `WHATSAPP_<contact>_<timestamp>.md`, `FILE_<original_name>`
- **Approval Files:** `APPROVAL_REQUIRED_<action>_<date>.md`
- **Briefings:** `YYYY-MM-DD_Day_Briefing.md`
- **Plans:** `Plan_<task>_<date>.md`

### Markdown Frontmatter Schema

All action files use YAML frontmatter:

```yaml
---
type: email|whatsapp|file_drop|approval_request|payment
from: sender@example.com
subject: Invoice Due
received: 2026-01-07T10:30:00Z
priority: high|medium|low
status: pending|in_progress|done|approved|rejected
---
```

### Coding Style (Python Watchers)

- Use `pathlib.Path` for file operations
- Implement `BaseWatcher` abstract class pattern
- Logging via `logging` module (not print)
- Graceful error handling with `try/except` in main loop
- Check interval: 30-120 seconds depending on watcher type

### Testing Practices

- Run `verify.py` before browser automation tasks
- Test watchers with sample inputs before deployment
- Validate MCP server connectivity before sensitive actions

## Tiered Achievement Levels

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian vault + Dashboard.md, one Watcher, Claude reading/writing vault, basic folder structure |
| **Silver** | 20-30h | 2+ Watchers, MCP server, HITL workflow, scheduling, Plan.md generation |
| **Gold** | 40+h | Full cross-domain integration, Odoo accounting, multiple MCPs, Ralph Wiggum loop, weekly briefings |
| **Platinum** | 60+h | Cloud deployment (24/7), Cloud/Local split (Cloud drafts, Local approves), vault sync, Odoo on VM |

## Security Rules

- **Secrets Never Sync:** `.env`, tokens, WhatsApp sessions, banking credentials stay local
- **Vault Sync:** Only markdown/state files sync between Cloud and Local
- **Single-Writer Rule:** Only Local writes to `Dashboard.md`
- **Cloud Writes:** Updates to `/Updates/` or `/Signals/` only
- **Approval Required:** Cloud can draft emails/social posts; Local must approve before send/post

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |
| Ralph loop stuck | Check if task file exists in `/Needs_Action/` or `/In_Progress/` |

## Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools Reference:** `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Agent Skills Documentation:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

## Weekly Research Meeting

- **When:** Wednesdays at 10:00 PM PKT
- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube (backup):** https://www.youtube.com/@panaversity
