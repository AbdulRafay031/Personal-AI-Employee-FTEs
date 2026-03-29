# Setup OpenRouter for Qwen Code API

This guide walks you through setting up OpenRouter API to power your AI Employee with Qwen Code.

## What is OpenRouter?

OpenRouter is a unified API that provides access to multiple AI models including Qwen. It offers:
- ✅ Easy setup (no phone verification)
- ✅ Pay-per-use pricing (~$0.50-2 per million tokens)
- ✅ OpenAI-compatible API (easy integration)
- ✅ Multiple Qwen model options

## Step 1: Get OpenRouter API Key

### 1.1 Create Account

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Click **Sign In** (top right)
3. Sign in with Google, GitHub, or Email

### 1.2 Add Credits

1. Click your profile icon → **Credits**
2. Add minimum $5 credit (recommended to start)
3. Payment via credit card or crypto

### 1.3 Create API Key

1. Go to [Keys page](https://openrouter.ai/keys)
2. Click **Create Key**
3. Give it a name (e.g., "AI Employee")
4. Copy the key immediately (you can't see it again!)

**Your key looks like:** `sk-or-v1-a1b2c3d4e5f6...`

## Step 2: Configure AI Employee

### 2.1 Install Python Dependencies

```bash
cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs"
pip install -r requirements.txt
```

### 2.2 Create .env File

Copy the example file and add your API key:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

### 2.3 Edit .env File

Replace the placeholder with your actual API key:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE

# Leave these as defaults
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
QWEN_MODEL=qwen/qwen-2.5-coder-32b-instruct
OPENROUTER_APP_NAME=AI Employee FTE
```

**Save the file.**

## Step 3: Test the Connection

### 3.1 Quick Test

Run a simple API test:

```bash
python -c "from openai import OpenAI; from dotenv import load_dotenv; import os; load_dotenv(); client = OpenAI(base_url=os.getenv('OPENROUTER_BASE_URL'), api_key=os.getenv('OPENROUTER_API_KEY')); print(client.chat.completions.create(model='qwen/qwen-2.5-coder-32b-instruct', messages=[{'role': 'user', 'content': 'Hello!'}]).choices[0].message.content)"
```

Expected output: A greeting from Qwen!

### 3.2 Test Orchestrator

```bash
# Run orchestrator once (doesn't loop)
python orchestrator.py AI_Employee_Vault --once
```

**Expected output:**
```
INFO - OpenRouter API configured (key: sk-or-v1-...)
INFO - Orchestrator initialized for vault: AI_Employee_Vault
INFO - Using model: qwen/qwen-2.5-coder-32b-instruct
INFO - Processing 0 tasks from Needs_Action
INFO - Sending request to Qwen (qwen/qwen-2.5-coder-32b-instruct)...
INFO - Qwen Code processed tasks successfully via OpenRouter API
```

## Step 4: Run AI Employee

### 4.1 Start File System Watcher (Terminal 1)

```bash
python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder test_drop
```

### 4.2 Start Orchestrator (Terminal 2)

```bash
# Continuous mode (checks every 60 seconds)
python orchestrator.py AI_Employee_Vault

# Or with custom interval
python orchestrator.py AI_Employee_Vault --interval 30
```

### 4.3 Test with a File

1. Drop a file into `test_drop/` folder
2. Watcher creates action file in `Needs_Action/`
3. Orchestrator sends task to Qwen via API
4. Qwen processes the task and creates Plan.md

## Available Qwen Models

| Model | Context | Price (1M tokens) | Best For |
|-------|---------|-------------------|----------|
| `qwen/qwen-2.5-coder-32b-instruct` | 32K | ~$0.50 | Code, general tasks |
| `qwen/qwen-plus` | 32K | ~$1.00 | Balanced performance |
| `qwen/qwen-max` | 32K | ~$2.00 | Complex reasoning |
| `qwen/qwen-turbo` | 32K | ~$0.20 | Fast, cheap tasks |

Change model in `.env`:
```env
QWEN_MODEL=qwen/qwen-2.5-coder-32b-instruct
```

## Troubleshooting

### "API key not configured"

**Problem:** `.env` file missing or API key not set

**Solution:**
```bash
# Check if .env exists
dir .env

# Verify API key is set
type .env
```

### "OpenAI package not installed"

**Problem:** Missing Python dependency

**Solution:**
```bash
pip install openai python-dotenv
```

### "Invalid API key"

**Problem:** Wrong key or key expired

**Solution:**
1. Go to [OpenRouter Keys](https://openrouter.ai/keys)
2. Delete old key, create new one
3. Update `.env` file

### "Insufficient credits"

**Problem:** Out of OpenRouter credits

**Solution:**
1. Go to [Credits page](https://openrouter.ai/credits)
2. Add more credits
3. Retry

### "Rate limit exceeded"

**Problem:** Too many requests too fast

**Solution:**
- Increase orchestrator interval: `--interval 120`
- Contact OpenRouter for higher limits

## Cost Estimation

**Typical usage per task:**
- Input: ~500-2000 tokens
- Output: ~500-3000 tokens
- **Cost per task: ~$0.001-0.01**

**Monthly estimate (100 tasks/day):**
- ~3000 tasks/month
- **~$3-30/month** depending on complexity

## Security Notes

- ✅ `.env` is in `.gitignore` - never commit it
- ✅ API key stored locally only
- ✅ All requests use HTTPS
- ✅ OpenRouter doesn't store your data

## Next Steps

1. ✅ Test with simple text files first
2. ✅ Review Qwen's output in `Plans/` folder
3. ✅ Adjust `Company_Handbook.md` rules as needed
4. ✅ Set up monitoring for API usage

## Resources

- [OpenRouter Docs](https://openrouter.ai/docs)
- [Qwen Models](https://openrouter.ai/models?q=qwen)
- [OpenAI Python Library](https://github.com/openai/openai-python)

---

*Last updated: 2026-03-30*
