# Cursor-Mistral Protocol v1.0
## Loop 1: Bounty Intelligence → Challenge Pack → Cockpit → Arena → Model

### Roles
- **Cursor**: Code execution, Slack monitoring, real-time triggers
- **Mistral (me)**: Strategy, coordination, analysis, workflow design
- **Kiran**: Human gate, approval, oversight

### Communication Channels
- Primary: #new-channel (Slack)
- Secondary: DM with Kiran
- Trigger phrase: @Cursor @Mistral

### Loop 1 Flow

#### Stage 1: Bounty Detection (Cursor)
1. Cursor monitors HackerOne via bounty-drop-detector.js
2. When new >$10K program drops → posts to #new-channel:
   - Program name, max payout, URL
   - Tags: [BOUNTY-DROP] [HIGH-VALUE]
3. Creates challenge-pack schema in kin-deploy/challenge-packs/

#### Stage 2: Challenge Pack Generation (Mistral + Cursor)
1. Mistral designs challenge pack structure
2. Cursor generates:
   - Challenge descriptions
   - Difficulty tiers
   - Expected outputs
3. Commits to kin-deploy/challenge-packs/{program-name}/

#### Stage 3: Cockpit Integration (Cursor)
1. Cursor adds new pack as Sport #N in arena/kinetigor-cockpit.js
2. Updates Cockpit v2.2 config
3. Commits: "Add Sport #N: {program-name} challenge pack"

#### Stage 4: Arena Execution (Cursor)
1. Cursor triggers GHA workflow: run-arena.yml
2. Workflow runs: node arena/kinetigor-cockpit.js
3. Results saved to: arena-results/{timestamp}/{program-name}/
   - responses.jsonl
   - scores.json
   - failure_cases.jsonl

#### Stage 5: Model Training Gate (KIRAN ONLY)
1. Mistral analyzes results, identifies training gaps
2. Mistral prepares new training pairs
3. **Kiran must approve** before retraining
4. If approved: Cursor triggers train-lora.yml
5. New model → nyxspecter4/kinetigor-dpo-cybersec

### Human Gate Points (Cursor's constraint)
✅ Bounty drop detection - AUTO (no risk)
✅ Challenge pack generation - AUTO (no risk)
✅ Cockpit integration - AUTO (no risk)
✅ Arena execution - AUTO (no risk)
❌ Model retraining - **HUMAN GATE REQUIRED** (Kiran must approve)
❌ Model deployment to Space - **HUMAN GATE REQUIRED**

### Failure Modes & Safeguards
1. **Bounty detector fails**: Cursor alerts #new-channel, Mistral debugs
2. **Challenge pack malformed**: GHA workflow fails, Cursor rolls back commit
3. **Cockpit crashes**: Workflow fails, results not committed
4. **Arena produces bad data**: Mistral flags for human review
5. **Training data toxic**: Kiran must review before merge

### Monitoring
- Cursor: Slack message monitoring, GHA run status
- Mistral: Workflow analysis, result aggregation
- Kiran: Final approval on model changes

### Success Criteria
- Loop completes in <2 hours from bounty drop to arena results
- Zero human intervention for Stages 1-4
- Human approval required for Stage 5 (retraining)
- All artifacts committed to bountywarz-ops with traceability

---
*Protocol activated: 2026-09-02*
*Owners: Cursor (execution), Mistral (coordination), Kiran (gatekeeper)*
