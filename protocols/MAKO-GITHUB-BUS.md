# 📖 MAKO-GITHUB-BUS Protocol v1.0

> **The rulebook. Read this once. Reference it forever.**

---

## Philosophy

**Chat is ephemeral. GitHub is forever.**

Every time you say "fix this" in chat, it dies when the chat scrolls.  
Every time you open a PR with the right template, **it is tracked, labeled, audited, and enforced.**

This protocol turns "I told Hermes" into **"Hermes ACK'd at 14:23, Mako verified."**

---

## The Core Loop

```
Meli discovers something → Opens sync PR → Labeled + auto-routed
                                              ↓
Hermes gets pinged ← Checks PR ← GitHub Actions bot
    ↓
Hermes ACKs (comments "ACK") → Mako records it → DONE
    ↓
Hermes ghosts for 4h → Escalation to Captain → INTERVENTION
```

---

## PR Naming Conventions

| PR Title Format | Meaning | Auto-Labels |
|----------------|---------|-------------|
| `[SYNC-10AM] Meli Status → Hermes` | Morning handoff | `sync/10am`, `comms/meli→hermes` |
| `[SYNC-6PM] Meli EOD → Hermes` | Evening handoff | `sync/6pm`, `comms/meli→hermes` |
| `[MERGE-ACK] Hermes → Meli: PR #142` | Merge confirmation | `comms/hermes→meli` |
| `[BLOCKER] Drone physics desync` | Critical issue | `priority/imperative` |
| `[QUESTION] Meli: Should we use X?` | Architecture question | `comms/meli→hermes` |

**Rule:** If you don't use the bracket prefix, the bot might miss it. Use the prefix.

---

## Timing Rules

| Event | Deadline | Enforcement |
|-------|----------|-------------|
| `[SYNC-10AM]` PR | Open by 10:00 GMT+8 | None (but Captain notices if missing) |
| `[SYNC-6PM]` PR | Open by 18:00 GMT+8 | Same |
| `priority/imperative` PR | ACK within 4 hours | 2h = gentle ping, 4h = escalate to Captain |
| Standard PR | ACK within 24 hours | 24h = Mako flags it |

---

## ACK Protocol

"ACK" means **I have read this and I am acting on it.**

### Valid ACK Formats (Hermes comments on PR):
```
ACK — merged, clean
ACK — reviewed, no issues
ACK — blocked by X, escalating
ACK — need Meli to clarify Y before I act
```

### Invalid (doesn't count):
```
ok
got it
👍
```
These are read receipts, not ACKs. **Mako does not count them.**

---

## Escalation Chain

```
Step 1: PR opened → Auto-labeled → Agent pinged (0h)
Step 2: 2 hours → Gentle reminder comment by bot
Step 3: 4 hours → `ack/missing` label added
Step 4: 4 hours → Captain @ mentioned in PR
Step 5: 8 hours → Captain DM / chat ping (Mako does this manually)
Step 6: 24 hours → Weekly health flag, pattern review
```

---

## Agent Responsibilities

### Meli
1. Open `[SYNC-10AM]` and `[SYNC-6PM]` every day
2. Use the template. Fill the template. Don't skip sections.
3. If something is imperative, say so in the body
4. Comment ACK on Hermes's replies

### Hermes
1. Watch the `comms/meli→hermes` label
2. ACK within 4 hours on imperative items
3. If you can't ACK, comment WHY ("in merge conflict, need 2 more hours")
4. Use `[MERGE-ACK]` PRs to confirm merges back to Meli

### Mako (me)
1. Audit every PR within 1 hour of opening
2. Comment with ACK status
3. Track patterns in `audit/`
4. Escalate ghosting
5. Weekly report: who missed what, how often

### Captain
1. Respond to escalations within 4 hours
2. Reassign blockers when needed
3. Review weekly health report

---

## Directory Guide

| Path | What It Is | Who Edits |
|------|-----------|-----------|
| `.github/PULL_REQUEST_TEMPLATE/meli-to-hermes.md` | Template for Meli | Captain (rarely) |
| `.github/PULL_REQUEST_TEMPLATE/hermes-to-meli.md` | Template for Hermes | Captain (rarely) |
| `.github/PULL_REQUEST_TEMPLATE/blocker-escalation.md` | Template for blockers | Captain (rarely) |
| `.github/workflows/sync-enforcer.yml` | The bot | Captain only |
| `protocols/MAKO-GITHUB-BUS.md` | This file | Captain only |
| `protocols/meli-onboarding.md` | Meli's quick start | Captain only |
| `audit/YYYY-MM-DD-mako-log.md` | Daily audit | Mako only |
| `audit/weekly-team-health.md` | Weekly summary | Mako only |

**Rule:** Agents don't edit protocol files. Only Captain does. Mako edits audit files.

---

## FAQ

**Q: What if there's nothing to sync?**  
A: Meli still opens the PR with body: "Nothing new since last sync. Next: [thing]." Empty syncs are data — they prove the system is alive.

**Q: What if Hermes is mid-merge and can't review?**  
A: He comments: "ACK — in active merge, will review at [time]." This resets the clock. Mako records it.

**Q: Can we use this for non-Meli/Hermes agents?**  
A: Yes. Add new templates. Add new labels. The system scales. But start with these two — they're the critical path.

**Q: What if a PR is urgent but not a sync?**  
A: Use `[BLOCKER]` prefix. It auto-gets `priority/imperative` and the 4-hour clock.

**Q: Does this replace chat?**  
A: No. Chat is for fast questions ("hey, what does this do?"). PRs are for things that MUST be tracked, verified, and completed.

---

## Version History

- **v1.0** — 2026-08-17 — Initial deployment

---

*Protocol enforced by MakoThoth-KClaw. Violations logged. Patterns reviewed. No exceptions without Captain approval.*
