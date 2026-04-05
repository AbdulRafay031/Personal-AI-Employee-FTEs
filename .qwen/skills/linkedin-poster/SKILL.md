# LinkedIn Poster Skill

Automate LinkedIn posts to generate business leads and share updates. Uses Playwright for browser automation with human-in-the-loop approval.

## Overview

This skill enables your AI Employee to:
- Draft LinkedIn posts based on business goals and achievements
- Schedule posts for optimal engagement times
- Auto-post approved content (with HITL approval)
- Track post performance metrics
- Maintain brand voice and consistency

## Architecture

```
Business Goals → AI Drafts Post → Human Approval → LinkedIn Poster → LinkedIn
                        ↓                ↓
                Plans/Plan_linkedin.md  Pending_Approval/LINKEDIN_POST_<date>.md
```

## ⚠️ Important Warnings

1. **LinkedIn Terms of Service:** Automated posting may violate LinkedIn ToS. Use at your own risk.
2. **Rate Limits:** Don't post more than 3-5 times per day to avoid account restrictions
3. **Authentication:** Session cookies must be kept secure and never synced to cloud
4. **Content Quality:** Always review AI-generated content for accuracy before posting

## Setup

### Prerequisites

1. **Playwright installed:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **LinkedIn account:** Active LinkedIn profile with posting permissions

3. **Session storage:** Create a folder for persistent browser session:
   ```bash
   mkdir -p /path/to/vault/.linkedin_session
   ```

4. **Business Goals configured:** Ensure `/Vault/Business_Goals.md` exists with:
   - Target audience
   - Brand voice guidelines
   - Content themes
   - Posting frequency goals

### Installation

```bash
# Install the skill (if using Qwen agent)
# Or manually copy this skill to your .qwen/skills/ directory

# Verify Playwright installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Usage

### Basic Usage

```bash
# Draft a post (no posting, just creates draft file)
python linkedin_poster.py /path/to/vault --action draft --topic "Q1 achievements"

# Post with approval workflow
python linkedin_poster.py /path/to/vault --action post --file "Plans/Plan_linkedin_20260107.md"

# Schedule recurring posts
python linkedin_poster.py /path/to/vault --action schedule --frequency weekly
```

### Command Line Options

```bash
python linkedin_poster.py /path/to/vault \
  --action draft|post|schedule|analytics \
  --topic "Your topic" \
  --file "path/to/plan.md" \
  --session-path /path/to/session \
  --headless \
  --frequency daily|weekly|monthly
```

| Option | Default | Description |
|--------|---------|-------------|
| `--action` | draft | Action: draft, post, schedule, analytics |
| `--topic` | None | Topic/theme for the post |
| `--file` | None | Path to approved plan file |
| `--session-path` | Required | Path to store LinkedIn session |
| `--headless` | False | Run browser in headless mode |
| `--frequency` | weekly | Posting frequency for scheduled posts |
| `--time` | 09:00 | Posting time (HH:MM format) |

## Post Types

### 1. Achievement Post

Celebrates business milestones:

```markdown
🎉 Excited to share that we've reached a major milestone!

This week, our team successfully [achievement]. This wouldn't have been possible without [key factors].

Key takeaways:
✅ Lesson 1
✅ Lesson 2
✅ Lesson 3

What's next? [Future plans]

#Milestone #Business #Growth
```

### 2. Educational Post

Shares knowledge and insights:

```markdown
💡 Here's something I've learned about [topic]...

[Insight/lesson content]

Many people think [common misconception], but in reality [truth].

Have you experienced this? Share your thoughts below! 👇

#Learning #ProfessionalDevelopment #Industry
```

### 3. Engagement Post

Asks questions to drive engagement:

```markdown
❓ Quick question for my network:

[Thought-provoking question related to your industry]

I'm curious to hear different perspectives. Drop your thoughts in the comments!

#Discussion #Community #ProfessionalNetwork
```

### 4. Promotional Post

Announces services/products (use sparingly):

```markdown
🚀 Big news! We're launching [product/service]...

After [time period] of development, we're finally ready to help [target audience] solve [problem].

Early bird offer: [special offer]

Interested? DM me or visit [link]

#Launch #Innovation #Solution
```

## Content Guidelines

### Brand Voice Configuration

Add to `Business_Goals.md`:

```markdown
## LinkedIn Content Strategy

### Brand Voice
- Tone: Professional yet approachable
- Style: Data-driven with personal insights
- Emoji usage: Moderate (2-4 per post)
- Hashtag strategy: 3-5 relevant hashtags

### Content Pillars
1. Industry insights (40%)
2. Company achievements (20%)
3. Educational content (25%)
4. Engagement posts (15%)

### Posting Schedule
- Frequency: 3-5 times per week
- Best times: 9:00 AM, 12:00 PM, 5:00 PM
- Timezone: PST

### Topics to Avoid
- Political opinions
- Controversial industry debates
- Competitor comparisons
```

### Hashtag Strategy

```markdown
### Core Hashtags (always use 1-2)
#Business #Professional #Industry

### Topic-Specific Hashtags (rotate)
#Technology #Innovation #Leadership #Growth #Strategy

### Trending Hashtags (monitor weekly)
Check LinkedIn trending topics before posting
```

## Approval Workflow

### Step 1: AI Drafts Post

```bash
# AI creates draft
python linkedin_poster.py /vault --action draft --topic "Weekly update"
```

Creates: `Plans/Plan_linkedin_YYYYMMDD.md`

```markdown
---
type: linkedin_draft
topic: Weekly update
created: 2026-01-07T10:00:00Z
status: pending_review
author: AI_Employee
---

## Post Content

🎉 This week's achievements:

✅ Completed Project Alpha milestone
✅ Onboarded 3 new clients
✅ Launched new website feature

Key metric: 25% increase in engagement

What's next? Scaling our automation systems!

#Business #Growth #Milestone

---

## Suggested Actions

- [ ] Review content for accuracy
- [ ] Edit tone/voice if needed
- [ ] Approve for posting (move to Approved/)
- [ ] Schedule for optimal time

---

## Notes

```
Add review notes here...
```
```

### Step 2: Human Review

1. Review draft in `Plans/` folder
2. Edit content if needed
3. Move to `Pending_Approval/` for posting approval

### Step 3: Create Approval Request

```markdown
---
type: approval_request
action: linkedin_post
content_hash: abc123...
created: 2026-01-07T10:30:00Z
scheduled_time: 2026-01-07T12:00:00Z
status: pending
---

## LinkedIn Post Approval

**Content Preview:**
[Post content here]

**Scheduled Time:** 2026-01-07 12:00 PM PST
**Post Type:** Achievement
**Estimated Reach:** 500-1000 impressions

---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.

## To Edit
Move back to Plans/ with edit notes.
```

### Step 4: Execute Post

```bash
# Orchestrator detects approved file and executes
python linkedin_poster.py /vault --action post --file "Approved/LINKEDIN_POST_20260107.md"
```

## Session Management

### First-Time Setup

1. Run in interactive mode:
   ```bash
   python linkedin_poster.py /vault --action login --session-path /path/to/session --interactive
   ```

2. Log in to LinkedIn manually in the browser window

3. Session saved to `/path/to/session/`

### Session Refresh

If session expires:
```bash
# Delete old session
rm -rf /path/to/session/*

# Re-authenticate
python linkedin_poster.py /vault --action login --session-path /path/to/session --interactive
```

### Session Security

- **NEVER sync session folder** to cloud (add to `.gitignore`)
- **NEVER share session files** (contains authentication cookies)
- Store session in secure location with restricted permissions

```bash
# Set restrictive permissions (Linux/Mac)
chmod 700 /path/to/linkedin_session
```

## Scheduling

### Optimal Posting Times

Based on LinkedIn engagement research:

| Day | Best Times (PST) |
|-----|------------------|
| Tuesday | 9:00 AM, 12:00 PM |
| Wednesday | 9:00 AM, 12:00 PM, 5:00 PM |
| Thursday | 9:00 AM, 12:00 PM |
| Friday | 9:00 AM, 11:00 AM |
| Monday | 10:00 AM, 12:00 PM |
| Weekend | Avoid (low engagement) |

### Schedule Configuration

Add to `Business_Goals.md`:

```markdown
## LinkedIn Schedule

- **Frequency:** 3 times per week
- **Preferred days:** Tuesday, Wednesday, Thursday
- **Preferred time:** 9:00 AM PST
- **Timezone:** America/Los_Angeles
- **Auto-post:** false (always require approval)
```

### Cron Schedule Example

```bash
# Run LinkedIn poster every Tuesday, Wednesday, Thursday at 8:00 AM
0 8 * * 2,3,4 cd /path/to/Personal-AI-Employee-FTEs && python linkedin_poster.py /vault --action scheduled-post
```

## Content Calendar

### Weekly Planning

Create `Plans/LinkedIn_Content_Calendar_YYYY_MM.md`:

```markdown
# LinkedIn Content Calendar - January 2026

## Week 1 (Jan 6-10)
- **Tue 1/7:** Achievement post (Q4 results)
- **Wed 1/8:** Educational (Industry trends)
- **Thu 1/9:** Engagement (Question for network)

## Week 2 (Jan 13-17)
- **Tue 1/14:** Promotional (New service launch)
- **Wed 1/15:** Educational (How-to guide)
- **Thu 1/16:** Achievement (Client success story)

## Themes for Month
- Primary: Growth & Innovation
- Secondary: Customer Success
- Hashtag focus: #Business2026 #Innovation
```

## Analytics Tracking

### Post Performance Metrics

Track in `Accounting/Social_Media_Analytics.md`:

```markdown
## LinkedIn Posts - January 2026

| Date | Content | Impressions | Likes | Comments | Shares | CTR |
|------|---------|-------------|-------|----------|--------|-----|
| Jan 7 | Q4 Achievement | 1,234 | 45 | 12 | 8 | 2.3% |
| Jan 8 | Industry Trends | 987 | 32 | 8 | 5 | 1.8% |

### Monthly Summary
- **Total Posts:** 12
- **Total Impressions:** 15,432
- **Average Engagement:** 3.2%
- **Top Performing:** [Post title]
- **Leads Generated:** 5
```

### Analytics Collection

```bash
# Collect analytics from recent posts
python linkedin_poster.py /vault --action analytics --days 30
```

## Integration with Orchestrator

### Automated Workflow

1. **Trigger:** Scheduled time or business goal update
2. **Draft Creation:** AI creates post draft in `Plans/`
3. **Approval:** Human reviews and approves
4. **Posting:** LinkedIn poster executes
5. **Logging:** Post details logged to analytics file
6. **Follow-up:** Monitor comments and engagement

### Example Flow

```
Business_Goals.md updated
        ↓
Orchestrator detects change
        ↓
Creates Plan_linkedin_post.md
        ↓
Human reviews and approves
        ↓
LinkedIn poster publishes
        ↓
Analytics updated
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Clear session, re-authenticate in interactive mode |
| Post not publishing | Check session validity, verify LinkedIn UI hasn't changed |
| Content formatting broken | Simplify formatting, avoid special characters |
| Rate limit error | Wait 24 hours, reduce posting frequency |
| Browser crashes | Increase `--timeout`, disable headless mode |
| Session expires quickly | Check for LinkedIn security notifications |

## Security Considerations

### ⚠️ Important Warnings

1. **Terms of Service:** LinkedIn automation may violate ToS. Use responsibly.

2. **Account Safety:**
   - Don't post more than 5 times per day
   - Vary posting times (don't post at exact same time daily)
   - Use realistic engagement patterns
   - Monitor account for warnings

3. **Privacy:**
   - Never share session cookies
   - Keep session files local (don't sync to cloud)
   - Use dedicated business account (not personal)

4. **Content Responsibility:**
   - Always review AI-generated content
   - Verify facts and claims
   - Ensure compliance with industry regulations

### Recommended Safeguards

```bash
# Add to .gitignore
.linkedin_session/
*.linkedin_cookies
session_storage/
```

```bash
# Set file permissions
chmod 600 /path/to/vault/.linkedin_session/*
```

## Advanced Configuration

### Custom Content Templates

Create `Templates/LinkedIn_Post_Templates.md`:

```markdown
## Template 1: Achievement

🎉 [Exciting news/Milestone alert]!

We've just [achievement]. This is significant because [why it matters].

Key highlights:
✅ [Point 1]
✅ [Point 2]
✅ [Point 3]

Thank you to [team/partners/customers] for making this possible!

#Achievement #Milestone #Business

---

## Template 2: Educational

💡 Let's talk about [topic]...

Many people believe [misconception], but here's the reality:

[Truth/insight]

Here's what I've learned from experience:
1. [Lesson 1]
2. [Lesson 2]
3. [Lesson 3]

What's your experience with [topic]? Share below! 👇

#Education #Learning #Professional
```

### Auto-Generate from Business Metrics

```python
# In orchestrator or custom script
def generate_achievement_post(metrics: dict) -> str:
    """Generate post from business metrics."""
    return f"""
🎉 This week's performance:

📈 Revenue: ${metrics['revenue']} (+{metrics['growth']}%)
👥 New clients: {metrics['new_clients']}
✅ Projects completed: {metrics['completed_projects']}

Proud of what we've accomplished!

#Business #Growth #Success
"""
```

## Testing

### Test Post Draft

```bash
# Create test draft
python linkedin_poster.py /vault --action draft --topic "Test post"

# Review generated file
cat Plans/Plan_linkedin_test_*.md
```

### Test Posting (Safe Mode)

```bash
# Run in dry-run mode (no actual post)
export LINKEDIN_DRY_RUN=true
python linkedin_poster.py /vault --action post --file "Approved/TEST_POST.md"
```

## Performance Tuning

### Optimize Browser Usage

```bash
# Run headless for production
python linkedin_poster.py /vault --headless

# Increase timeout for slow connections
export LINKEDIN_TIMEOUT=60000
```

### Resource Usage

- **Memory:** ~250MB per browser instance
- **CPU:** <5% when idle, spikes during posting
- **Network:** Minimal (only during login and posting)

## Example Deployment

### Systemd Service (Linux)

```ini
# /etc/systemd/system/linkedin-poster.service
[Unit]
Description=LinkedIn Poster for AI Employee
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/Personal-AI-Employee-FTEs
ExecStart=/usr/bin/python3 linkedin_poster.py /path/to/vault --action scheduled-post
Environment="LINKEDIN_SESSION_PATH=/path/to/session"
```

```bash
# Run daily at 8 AM
0 8 * * * /usr/bin/systemctl start linkedin-poster.service
```

## Metrics & Monitoring

### Log File Location

```
/vault/Logs/linkedin_poster_YYYYMMDD.log
```

### Key Metrics to Monitor

- Posts published per week
- Approval rate (approved vs rejected)
- Average engagement per post
- Session expiry events
- Error rate

### Sample Log Output

```
2026-01-07 09:00:00 - LinkedInPoster - INFO - Starting LinkedInPoster
2026-01-07 09:00:05 - LinkedInPoster - INFO - Browser initialized
2026-01-07 09:00:10 - LinkedInPoster - INFO - Logged in successfully
2026-01-07 09:00:15 - LinkedInPoster - INFO - Post published successfully
2026-01-07 09:00:16 - LinkedInPoster - INFO - Analytics updated
```

## API Reference

### LinkedInPoster Class

```python
class LinkedInPoster:
    def __init__(self, vault_path: str, session_path: str, **kwargs)
    def login(self) -> bool
    def create_post(self, content: str) -> bool
    def get_analytics(self, days: int = 30) -> dict
    def schedule_post(self, content: str, scheduled_time: datetime) -> bool
```

### Post Content Format

```python
{
    'text': str,              # Main post content
    'hashtags': List[str],    # Hashtags to include
    'scheduled_time': str,    # ISO format datetime
    'post_type': str,         # achievement, educational, etc.
    'status': str,            # draft, approved, posted
}
```

## Related Skills

- **browsing-with-playwright:** Core browser automation
- **whatsapp-watcher:** Incoming message monitoring
- **gmail-watcher:** Email integration
- **email-mcp:** Send follow-up emails

## Next Steps

After setting up LinkedIn poster:
1. Configure brand voice in Business_Goals.md
2. Create content calendar for the month
3. Set up approval workflow
4. Schedule recurring posts
5. Monitor analytics and adjust strategy
6. Consider integrating with Twitter/X and Facebook

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
