# 🎓 Meli Onboarding — MAKO-GITHUB-BUS

> **Hey Meli! This is how you use the new system. One page. Read it once. You're in.**

---

## What Changed

Before: You tell Hermes stuff in chat. It gets lost.  
**Now: You tell Hermes stuff in a PR. It is tracked, labeled, audited, and enforced.**

Captain is tired of "I told Hermes and nothing happened."  
This fixes that.

---

## Your Job (2 PRs Per Day)

### 1. Morning Sync — `[SYNC-10AM]`

**When:** By 10:00 AM GMT+8  
**Template:** [meli-to-hermes.md](../.github/PULL_REQUEST_TEMPLATE/meli-to-hermes.md)

```
Title: [SYNC-10AM] Meli Status → Hermes — 2026-08-17
```

**What to put in it:**
- What you built since yesterday evening
- What needs Hermes to merge / review
- Any blockers
- What's next

**Example:**
```markdown
## What Changed
- Benchmarked drone physics at 60fps, 2% CPU overhead
- Updated territory control scoring algorithm
- Found edge case: 3+ drones in same zone causes desync

## Why Hermes Needs to See This
- The desync edge case blocks multiplayer stability. Needs fix before beta.

## Action Required
- [ ] Review territory scoring PR #138
- [ ] Merge if benchmarks pass
- [ ] Comment ACK when done

## Blockers
- Drone desync needs Kimi's eyes too. Not a Hermes fix.

## Next Sync Preview
- Running full multiplayer stress test tonight
- Will have results for tomorrow's 10am sync
```

### 2. Evening Sync — `[SYNC-6PM]`

**When:** By 6:00 PM GMT+8  
**Same template.** Same rules.

**What to put in it:**
- Wrap-up of day's work
- Did Hermes handle the morning sync? (Check the PR)
- Tomorrow's plan
- Anything urgent before end of day

---

## How to Open a Sync PR

### Step 1: Go to `bountywarz-ops` repo

https://github.com/nyxspecter4/bountywarz-ops

### Step 2: Click "New Pull Request"

### Step 3: Use the Template

When you open the PR, GitHub will auto-show the template. **Don't delete it.** Fill it in.

### Step 4: Use the Right Title

```
[SYNC-10AM] Meli Status → Hermes — 2026-08-17
[SYNC-6PM] Meli EOD Handoff → Hermes — 2026-08-17
```

**The bracket prefix is IMPORTANT.** The bot reads it and auto-labels your PR.

### Step 5: Submit

The bot will:
- Auto-label it `comms/meli→hermes` + `sync/10am` (or `sync/6pm`)
- Ping Hermes
- Start the 4-hour countdown
- Mako will audit it within the hour

---

## What Happens Next

| Time | What Happens |
|------|-------------|
| 0 min | You submit PR. Bot labels it. Hermes gets notified. |
| 2 hours | If Hermes hasn't ACK'd, bot pokes him gently. |
| 4 hours | If still no ACK, bot adds `ack/missing` label and @ mentions Captain. |
| You don't have to do anything | The system enforces itself. |

---

## Rules to Remember

1. **Use the template.** Don't freestyle. The template is the protocol.
2. **Use the bracket prefix** in the title. `[SYNC-10AM]`, `[SYNC-6PM]`, `[BLOCKER]`
3. **If it's imperative, say so.** Write "BLOCKS BETA" or "CRITICAL" in the body.
4. **Comment ACK on Hermes's replies.** Close the loop.
5. **Even if nothing changed, open the sync.** Write "No updates since last sync." This proves the bus is alive.

---

## Quick Reference: Title Prefixes

| Prefix | Use When | Example |
|--------|----------|---------|
| `[SYNC-10AM]` | Morning handoff | `[SYNC-10AM] Meli Status → Hermes` |
| `[SYNC-6PM]` | Evening handoff | `[SYNC-6PM] Meli EOD → Hermes` |
| `[BLOCKER]` | Something is stuck | `[BLOCKER] Drone desync in 3+ player zones` |
| `[QUESTION]` | Need Hermes's opinion | `[QUESTION] Should we use WebRTC or WebTransport?` |

---

## FAQ

**Q: What if Hermes ACKs but doesn't actually do the work?**  
A: Mako catches that. ACK means "I read it AND I'm acting." If he ACKs and nothing happens, that's a separate violation and I flag it.

**Q: What if I'm sick and miss a sync?**  
A: One miss is fine. Pattern of misses = I report it to Captain. The bus needs to stay alive.

**Q: Can I edit the template?**  
A: No. Captain edits templates. You fill them in.

**Q: What if the sync is super short?**  
A: That's fine. Bullet points. One sentence per item. Speed > length.

**Q: What about weekends?**  
A: Captain decides. If beta is close, syncs might be daily. If not, maybe weekdays only. Captain will tell you.

---

## You're Ready

1. Bookmark this page
2. Bookmark the [meli-to-hermes template](../.github/PULL_REQUEST_TEMPLATE/meli-to-hermes.md)
3. Open your first `[SYNC-10AM]` PR

**The system only works if you use it. One missed sync breaks the chain. Don't break the chain.** 🔗

---

*Welcome to the bus, Meli. No more lost messages.*  
*— MakoThoth-KClaw*
