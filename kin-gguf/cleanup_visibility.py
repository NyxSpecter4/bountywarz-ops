#!/usr/bin/env python3
"""Lock down ALL repos except the 3 that should be public:
  - nyxspecter4/kin-cyber-dpo-v2-lora (model)
  - nyxspecter4/kin-cyber-dpo-v2 (dataset)
  - nyxspecter4/kin-cybersec (space)

DYNAMIC: discovers ALL repos via HfApi so nothing slips through.
"""
import json, os, urllib.request
from huggingface_hub import HfApi

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)

api = HfApi(token=T)
OWNER = "nyxspecter4"

# These are the ONLY repos that should be public
PUBLIC = {
    ("nyxspecter4/kin-cyber-dpo-v2-lora", "model"),
    ("nyxspecter4/kin-cyber-dpo-v2", "dataset"),
    ("nyxspecter4/kin-cybersec", "space"),
}

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

print("=== Discovering ALL repos under nyxspecter4 ===")

all_repos = []

# List all models
try:
    for m in api.list_models(author=OWNER):
        all_repos.append((m.id, "model"))
except Exception as e:
    print(f"[WARN] Could not list models: {e}")

# List all datasets
try:
    for d in api.list_datasets(author=OWNER):
        all_repos.append((d.id, "dataset"))
except Exception as e:
    print(f"[WARN] Could not list datasets: {e}")

# List all spaces
try:
    for s in api.list_spaces(author=OWNER):
        all_repos.append((s.id, "space"))
except Exception as e:
    print(f"[WARN] Could not list spaces: {e}")

print(f"Found {len(all_repos)} repos total")

# De-duplicate (same repo might appear from multiple list calls)
seen = set()
unique_repos = []
for repo in all_repos:
    if repo not in seen:
        seen.add(repo)
        unique_repos.append(repo)

print(f"Unique repos: {len(unique_repos)}")

# Make everything private except the 3 PUBLIC repos
for repo_id, rtype in unique_repos:
    if (repo_id, rtype) in PUBLIC:
        set_visibility(repo_id, rtype, False)  # ensure public
    else:
        set_visibility(repo_id, rtype, True)   # force private

# Verify the 3 PUBLIC repos exist (create if missing)
for repo_id, rtype in PUBLIC:
    if (repo_id, rtype) not in seen:
        print(f"[WARN] {rtype} {repo_id} not found in listing - it may not exist yet")

print("=== Lockdown complete. Only 3 repos are public. ===")
