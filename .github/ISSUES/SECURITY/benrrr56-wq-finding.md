## 🚨 Security Finding from External Researcher

**Researcher:** @benrrr56-wq  
**Source:** [monk-io/monk-plugin#395](https://github.com/monk-io/monk-plugin/issues/395)  
**Severity:** HIGH  
**Status:** Acknowledged, Spec in Progress

---

## 📋 Finding Summary

benrrr56-wq identified that our **verb-class gating** is insufficient for **data-class surfaces** that return secrets:

- `monk.secret.list` → returns all secrets
- `monk.credentials.status` → returns credential state  
- `monk.workload.logs` → may contain sensitive data

**The Gap:** WebFetch → secret.list → chat **bypasses all gating** because these tools fall outside our verb-class gate set.

---

## 🎯 Proposed Solution

Implement **per-tool sensitivity classification** (independent of verb class):

1. **Data-class tags** on each tool (returns-secrets vs safe)
2. **Automatic gating** based on data-class + verb-class
3. **Audit logging** of all secret-returning calls

---

## 📊 Current State

- ✅ Verb-class gating implemented
- ❌ No data-class sensitivity classification
- ❌ No per-tool secret-return tracking
- ❌ No audit log of which tool returned which secret

---

## 🤝 Collaboration

We've reached out to @benrrr56-wq for collaboration on the spec. Their expertise is valuable for designing a robust gating matrix.

---

## 📅 Timeline

Targeting **Monday release** per RACE_PLAYBOOK.md cadence.

---

*Auto-generated from external security researcher finding*
