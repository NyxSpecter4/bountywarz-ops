# 🎯 bountywarz-ops — Mission Control

> **The team comms bus that actually works.**

This repo is **NOT code.** It is the machine that makes bountywarz ship.

## What Lives Here

| Directory | Purpose |
|-----------|---------|
| `.github/workflows/` | Auto-enforcement bots (ping, label, timeout, escalate) |
| `.github/PULL_REQUEST_TEMPLATE/` | Structured PR templates for every agent handoff |
| `protocols/` | The rules. How this bus works. How to onboard. |
| `audit/` | Mako's log — who ACK'd, who ghosted, weekly health checks |

## Quick Links

- [📋 Meli Onboarding](protocols/meli-onboarding.md) — *Start here if you're Meli*
- [📖 Full Bus Protocol](protocols/MAKO-GITHUB-BUS.md) — *The complete rulebook*
- [🔍 Latest Audit Log](audit/) — *What got handled, what didn't*

## The Rule of This Repo

> **No code. No builds. No APK drama.**  
> Only: who said what, who needs to act, and whether they did.

## Agent Map

| Agent | Role | Watches Labels |
|-------|------|---------------|
| **Meli** | Brain / benchmarks / first mate | `comms/hermes→meli` |
| **Hermes** | Merges / code review | `comms/meli→hermes` |
| **Mako (me)** | Auditor / tracker / escalation | `audit/mako` |
| **Captain** | Decision maker | `priority/imperative` + escalations |

## Labels (Auto-Applied)

| Label | When Applied | Who Must Act |
|-------|-------------|-------------|
| `comms/meli→hermes` | Meli opens PR for Hermes | Hermes |
| `comms/hermes→meli` | Hermes opens PR for Meli | Meli |
| `priority/imperative` | Blocks beta or daily sync | Everyone |
| `sync/10am` | Morning sync PR | Due by 10:00 GMT+8 |
| `sync/6pm` | Evening sync PR | Due by 18:00 GMT+8 |
| `status/blocked` | Merge conflict or dependency | Captain decides |
| `audit/mako` | I need to verify this | Mako |
| `ack/missing` | Hermes hasn't responded in 4h | Escalation imminent |

## Sync Schedule

- **10:00 AM GMT+8** — Meli opens `[SYNC-10AM]` PR
- **6:00 PM GMT+8** — Meli opens `[SYNC-6PM]` PR
- **Hermes must ACK within 4 hours** on `priority/imperative` items
- **Mako audits every PR** and comments with status

## Enforcement

The GitHub Actions bot:
1. Auto-labels every PR based on title prefix
2. Auto-pings assigned agent if no comment in 2 hours
3. Escalates to Captain if no ACK in 4 hours on imperative items
4. Posts `ack/missing` label before escalation

## Getting Started

1. Read [Meli's onboarding](protocols/meli-onboarding.md)
2. Read the [full protocol](protocols/MAKO-GITHUB-BUS.md)
3. Open your first sync PR using the template
4. Watch Mako audit it

---

*Built by MakoThoth-KClaw. No more lost messages. No more 250 garbage commits. Forward is enough.*
