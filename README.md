# AI Employee FTE - Bronze Tier Implementation

A local-first, agent-driven autonomous AI employee system built with Qwen Code and Obsidian.

## 🎯 Bronze Tier Deliverables

This implementation includes all Bronze Tier requirements:

- ✅ **Obsidian Vault** with Dashboard.md and Company_Handbook.md
- ✅ **File System Watcher** - Monitors drop folder for new files
- ✅ **Gmail Watcher** - Monitors Gmail for new messages (optional setup)
- ✅ **Claude Code Integration** - Reads from and writes to the vault
- ✅ **Basic Folder Structure** - Inbox, Needs_Action, Done, etc.
- ✅ **Orchestrator** - Master process coordinating all components

## 📁 Project Structure

```
Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/          # Obsidian vault (open this in Obsidian)
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Inbox/                  # Raw incoming files
│   ├── Needs_Action/           # Pending tasks
│   ├── In_Progress/            # Tasks being worked on
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Ready for execution
│   ├── Rejected/               # Declined actions
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # Generated plans
│   ├── Accounting/             # Financial records
│   ├── Briefings/              # CEO briefings
│   └── Logs/                   # Audit logs
├── watchers/
│   ├── base_watcher.py         # Base class for all watchers
│   ├── gmail_watcher.py        # Gmail monitoring
│   └── filesystem_watcher.py   # File drop monitoring
├── orchestrator.py             # Master coordination process
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** - [Download](https://www.python.org/downloads/)
2. **Qwen Code** - Install via your preferred method
3. **Obsidian** - [Download](https://obsidian.md/download)
4. **Node.js v24+** (optional, for MCP servers) - [Download](https://nodejs.org/)

### Step 1: Install Python Dependencies

```bash
cd Personal-AI-Employee-FTEs
pip install -r requirements.txt
```

**Note:** For Gmail integration, also install:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 2: Setup Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder
4. Review `Dashboard.md`, `Company_Handbook.md`, and `Business_Goals.md`

### Step 3: Configure Qwen Code API (Required for AI Automation)

To enable automatic task processing with Qwen Code:

1. **Get OpenRouter API Key:**
   - Go to [OpenRouter.ai](https://openrouter.ai/)
   - Sign up and add credits (minimum $5)
   - Create API key at [Keys page](https://openrouter.ai/keys)

2. **Create .env file:**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit with your API key
   notepad .env
   ```

3. **Add your API key:**
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
   ```

**Full setup guide:** See [setup_openrouter.md](./setup_openrouter.md)

### Step 4: Configure Gmail Watcher (Optional)

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Authenticate:**
   ```bash
   python watchers/gmail_watcher.py AI_Employee_Vault --credentials /path/to/credentials.json --auth-only
   ```

3. **Token saved:** `AI_Employee_Vault/token.json` (add to `.gitignore`!)

### Step 6: Create Drop Folder

Create a folder where you'll drop files for processing:

```bash
# Windows
mkdir C:\Users\YourName\AI_Drop

# Mac/Linux
mkdir ~/AI_Drop
```

### Step 7: Start the Watchers

**Terminal 1 - File System Watcher:**
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder /path/to/drop/folder
```

**Terminal 2 - Gmail Watcher (if configured):**
```bash
python watchers/gmail_watcher.py AI_Employee_Vault --credentials /path/to/credentials.json
```

**Terminal 3 - Orchestrator:**
```bash
python orchestrator.py AI_Employee_Vault
```

### Step 8: Test the System

1. **Drop a file** into your watch folder
2. **Watch** as an action file is created in `Needs_Action/`
3. **Run Qwen Code** manually (for Bronze tier):
   ```bash
   cd AI_Employee_Vault
   qwen
   ```
4. **Prompt Qwen:** "Check the Needs_Action folder and process any pending tasks"
5. **Review** the output and move completed tasks to `Done/`

## 📋 Usage Guide

### How Tasks Flow Through the System

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gmail     │────▶│   Watchers   │────▶│ Needs_Action│────▶│   Qwen      │
│   Drop File │     │  (Python)    │     │   Folder    │     │   Code      │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Done      │◀────│   Approved   │◀────│   Pending   │◀────│   Plan.md   │
│   Folder    │     │   Folder     │     │  Approval   │     │   Created   │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, new contacts):

1. Qwen creates a file in `Pending_Approval/`
2. **You review** the file contents
3. **Move to `Approved/`** to execute, or `Rejected/` to decline
4. Orchestrator executes approved actions

### File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Email | `EMAIL_<sender>_<id>.md` | `EMAIL_john@example.com_12345.md` |
| WhatsApp | `WHATSAPP_<contact>_<date>.md` | `WHATSAPP_ClientA_20260107.md` |
| File Drop | `FILE_<original_name>_<timestamp>.md` | `FILE_invoice.pdf_20260107120000.md` |
| Plan | `PLAN_<task>_<date>.md` | `PLAN_invoice_client_a_20260107.md` |
| Approval | `APPROVAL_<action>_<date>.md` | `APPROVAL_payment_vendor_20260107.md` |

## 🔧 Configuration

### Watcher Intervals

Adjust how often watchers check for updates:

```bash
# File System Watcher (default: 30 seconds)
python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder ~/AI_Drop --interval 60

# Gmail Watcher (default: 120 seconds)
python watchers/gmail_watcher.py AI_Employee_Vault --credentials credentials.json --interval 300
```

### Orchestrator Settings

```bash
# Custom check interval (default: 60 seconds)
python orchestrator.py AI_Employee_Vault --interval 120

# Use different model
python orchestrator.py AI_Employee_Vault --model qwen-code

# Run once (for testing)
python orchestrator.py AI_Employee_Vault --once
```

## 🛠️ Troubleshooting

### Qwen Code Not Found

```bash
# Install Qwen Code (adjust based on your installation method)
# Example: pip install qwen-code
# Or use the Qwen Code CLI from your provider

# Verify installation
qwen --version
```

### Watcher Crashes

Check logs in `AI_Employee_Vault/Logs/`:
- `watcher_YYYYMMDD.log` - Watcher logs
- `orchestrator_YYYYMMDD.log` - Orchestrator logs

### Gmail Authentication Fails

```bash
# Delete old token and re-authenticate
rm AI_Employee_Vault/token.json
python watchers/gmail_watcher.py AI_Employee_Vault --credentials credentials.json --auth-only
```

### File Not Being Processed

1. Check file is in correct drop folder
2. Verify watcher is running (check logs)
3. Ensure file doesn't start with `.` or `~`
4. Check file hash isn't in `.processed_files`

## 📊 Bronze Tier Completion Checklist

| Requirement | Status | Location |
|-------------|--------|----------|
| Obsidian vault created | ✅ | `AI_Employee_Vault/` |
| Dashboard.md | ✅ | `AI_Employee_Vault/Dashboard.md` |
| Company_Handbook.md | ✅ | `AI_Employee_Vault/Company_Handbook.md` |
| Business_Goals.md | ✅ | `AI_Employee_Vault/Business_Goals.md` |
| File System Watcher | ✅ | `watchers/filesystem_watcher.py` |
| Gmail Watcher | ✅ | `watchers/gmail_watcher.py` |
| Folder structure | ✅ | All folders created |
| Qwen integration | ✅ | Via orchestrator + manual trigger |
| Documentation | ✅ | This README |

## 🚀 Next Steps (Silver Tier)

To progress to Silver Tier, add:

1. **WhatsApp Watcher** - Monitor WhatsApp Web for messages
2. **MCP Server Integration** - Auto-send emails via MCP
3. **Automated Claude Trigger** - Run Claude automatically when tasks arrive
4. **Human-in-the-Loop Workflow** - Full approval → execution pipeline
5. **Scheduled Tasks** - Cron-based daily briefings

## 📝 Security Notes

- **Never commit** `token.json`, `.env`, or credentials
- Add to `.gitignore`:
  ```
  AI_Employee_Vault/token.json
  AI_Employee_Vault/.processed_files
  AI_Employee_Vault/Logs/
  .env
  ```
- Review `Company_Handbook.md` for approval thresholds
- Enable audit logging in `AI_Employee_Vault/Logs/`

## 📚 Resources

- [Main Hackathon Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM)
- [Obsidian Help](https://help.obsidian.md/)
- [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)

## 🤝 Support

Join the weekly research meeting:
- **When:** Wednesdays at 10:00 PM PKT
- **Zoom:** [Join Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity Channel](https://www.youtube.com/@panaversity)

---

*Built for the Personal AI Employee Hackathon 2026*  
*Bronze Tier Implementation - January 2026*
