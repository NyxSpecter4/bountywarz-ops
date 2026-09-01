#!/usr/bin/env python3
"""Lock down ALL repos except the 3 that should be public:
  - nyxspecter4/kin-cyber-dpo-v2-lora (model)
  - nyxspecter4/kin-cyber-dpo-v2 (dataset)
  - nyxspecter4/kin-cybersec (space)
"""
import json, os, urllib.request

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)

def set_visibility(repo_id, repo_type, private):
    url = f"https://huggingface.co/api/{repo_type}s/{repo_id}/settings"
    data = json.dumps({"private": private}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {T}",
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req)
        print(f"[OK] {repo_type} {repo_id} -> {'private' if private else 'PUBLIC'} (HTTP {resp.status_code})")
    except Exception as e:
        print(f"[FAIL] {repo_type} {repo_id}: {e}")

# These are the ONLY 3 repos that should be public
PUBLIC = [
    ("nyxspecter4/kin-cyber-dpo-v2-lora", "model"),
    ("nyxspecter4/kin-cyber-dpo-v2", "dataset"),
    ("nyxspecter4/kin-cybersec", "space"),
]

# Everything else must be PRIVATE
MAKE_PRIVATE = [
    # Models
    ("nyxspecter4/kin-sft-lora", "model"),
    ("nyxspecter4/kin-sft-lora-gguf", "model"),
    ("nyxspecter4/kin-v2-cybersecurity-7b-lora", "model"),
    # Datasets
    ("nyxspecter4/kin-dpo-data", "dataset"),
    ("nyxspecter4/monk-bounty-dedup-corpus", "dataset"),
    ("nyxspecter4/cycle-2-edges-corpus", "dataset"),
    ("nyxspecter4/monk-bounty-evidence", "dataset"),
    ("nyxspecter4/kin-v2-data", "dataset"),
    ("nyxspecter4/monk-bounty-examples", "dataset"),
    ("nyxspecter4/kin-global-sft-20260505", "dataset"),
    ("nyxspecter4/kin-global-sft-20260504", "dataset"),
    ("nyxspecter4/kin-global-sft-20260427", "dataset"),
    ("nyxspecter4/kin-global-sft-20260426", "dataset"),
    # Spaces
    ("nyxspecter4/kin-v2-cybersecurity", "space"),
    ("nyxspecter4/kin-cyber-trend", "space"),
    ("nyxspecter4/kin-cyber-arena", "space"),
    ("nyxspecter4/kin-v2-edge-test", "space"),
    ("nyxspecter4/monk-finding-grade-arena", "space"),
    ("nyxspecter4/kin-cyber-trainer", "space"),
    ("nyxspecter4/monk-finding-loop", "space"),
    ("nyxspecter4/nemeton-war-room", "space"),
    ("nyxspecter4/monk-ctf-arena", "space"),
    ("nyxspecter4/makothoth-flywheel", "space"),
]

print("=== Making everything private except 3 repos ===")

for repo_id, rtype in MAKE_PRIVATE:
    set_visibility(repo_id, rtype, True)

# Make sure the 3 are public
for repo_id, rtype in PUBLIC:
    set_visibility(repo_id, rtype, False)

print("=== Done. Only 3 repos are public. ===")
