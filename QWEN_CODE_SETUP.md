# Using Qwen Code with AI Employee FTE

## Overview

This system is configured to use **Qwen Code** as the AI reasoning engine instead of Claude Code.

## Qwen Code Setup

### Option 1: Qwen Code CLI

If you have the Qwen Code CLI installed:

```bash
# Verify installation
qwen --version

# Run Qwen Code in the vault directory
cd AI_Employee_Vault
qwen
```

### Option 2: Qwen API

If you're using Qwen via API:

```bash
# Set your API key
export QWEN_API_KEY="your-api-key-here"

# Use the API client
python -c "from qwen import Qwen; print(Qwen().chat('Hello'))"
```

### Option 3: Local Qwen Model

If running Qwen locally (e.g., via Ollama, LM Studio):

```bash
# Example with Ollama
ollama run qwen2.5-coder:32b

# Example with LM Studio
# Start LM Studio server and use OpenAI-compatible API
```

## Integration with Orchestrator

The orchestrator is configured to use Qwen Code by default:

```bash
# Run orchestrator with Qwen Code
python orchestrator.py AI_Employee_Vault --model qwen-code
```

### If Qwen Code CLI is Not Available

The orchestrator will gracefully degrade to manual mode:
- Tasks are logged for manual processing
- You can process tasks manually in Obsidian
- All automation (watchers, file management) still works

## Manual Task Processing with Qwen Code

If automatic triggering isn't available, process tasks manually:

### Step 1: Check Needs_Action Folder

```bash
cd AI_Employee_Vault/Needs_Action
dir
```

### Step 2: Launch Qwen Code

```bash
cd AI_Employee_Vault
qwen
```

### Step 3: Prompt Qwen Code

```
I have tasks in the Needs_Action folder that need processing.

Please:
1. Read each task file in Needs_Action/
2. Create a Plan.md for complex multi-step tasks
3. Request approval for sensitive actions (payments > $100, new vendors)
4. Move completed tasks to the Done folder
5. Update the Dashboard.md

Remember to follow the rules in Company_Handbook.md.
```

### Step 4: Review Output

Qwen Code will:
- Analyze each task
- Create plans in `Plans/` folder
- Create approval requests in `Pending_Approval/`
- Update `Dashboard.md`

## Example Workflow

### Processing an Invoice

**Input:** `Needs_Action/FILE_invoice.pdf_....md`

**Qwen Code Output:**

1. **Creates Plan:**
   ```markdown
   # Plans/PLAN_invoice_vendor_20260330.md
   - [x] Extract vendor name: Acme Corp
   - [x] Extract amount: $500
   - [ ] Log to Accounting/Current_Month.md
   - [ ] Create approval request (amount > $100)
   ```

2. **Creates Approval Request:**
   ```markdown
   # Pending_Approval/APPROVAL_payment_acme_20260330.md
   Amount: $500
   Vendor: Acme Corp
   Due: 2026-04-30
   ```

3. **Updates Accounting:**
   ```markdown
   # Accounting/Current_Month.md
   | Date | Vendor | Amount | Status |
   |------|--------|--------|--------|
   | 2026-03-30 | Acme Corp | $500 | Pending |
   ```

## Configuration

### Custom Model Name

If your Qwen Code installation uses a different command:

```bash
# Edit orchestrator.py and change:
self.model = 'your-custom-model-name'

# Or pass via CLI:
python orchestrator.py AI_Employee_Vault --model your-model
```

### System Prompt

The default system prompt for Qwen Code:

```
You are an AI Employee assistant. Process tasks from the Needs_Action folder.
Follow the Company_Handbook.md rules.
Create Plan.md files for complex tasks.
Request approval for sensitive actions.
Move completed tasks to Done folder.
```

## Troubleshooting

### "qwen: command not found"

Qwen Code CLI is not installed or not in PATH.

**Solutions:**
1. Install Qwen Code CLI
2. Use manual mode (process tasks yourself)
3. Configure API-based access

### Tasks Not Being Processed

Check orchestrator logs:

```bash
# View latest logs
type AI_Employee_Vault\Logs\orchestrator_*.log
```

Expected log entry:
```
INFO - Qwen Code processed tasks successfully
```

Or if not available:
```
WARNING - Qwen Code CLI not found. Using manual mode.
```

## Alternative: Use Qwen via Web Interface

If CLI is not available:

1. Open Qwen web interface
2. Copy task content from `Needs_Action/*.md`
3. Paste and prompt Qwen
4. Copy output back to vault

## Best Practices

1. **Review before executing:** Always review Qwen Code's plans before approving
2. **Start small:** Test with simple tasks first
3. **Update handbook:** Refine Company_Handbook.md based on Qwen's decisions
4. **Monitor logs:** Check logs regularly for issues
5. **Backup vault:** Use Git or cloud sync for vault backup

## Resources

- [Qwen GitHub](https://github.com/QwenLM)
- [Qwen Documentation](https://qwen.readthedocs.io/)
- [Qwen Models on HuggingFace](https://huggingface.co/Qwen)

---

*Last updated: 2026-03-30*
