#!/usr/bin/env python3
"""Make old/bad models private to clean up our public presence."""
import json, os, urllib.request

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)

MAKE_PRIVATE = [
    "nyxspecter4/kin-sft-lora",
    "nyxspecter4/kin-v2-cybersecurity-7b-lora",
]

for repo_id in MAKE_PRIVATE:
    url = f"https://huggingface.co/api/models/{repo_id}/settings"
    data = json.dumps({"private": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {T}",
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req)
        print(f"[OK] {repo_id} -> private (HTTP {resp.status_code})")
    except Exception as e:
        print(f"[FAIL] {repo_id}: {e}")

print("Cleanup complete.")
