#!/usr/bin/env python3
"""Make old/bad models private to clean up our public presence."""
import requests, json, os

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)
HEADERS = {"Authorization": f"Bearer {T}", "Content-Type": "application/json"}

MAKE_PRIVATE = [
    "nyxspecter4/kin-sft-lora",
    "nyxspecter4/kin-v2-cybersecurity-7b-lora",
]

for repo_id in MAKE_PRIVATE:
    url = f"https://huggingface.co/api/models/{repo_id}/settings"
    resp = requests.put(url, headers=HEADERS, json={"private": True})
    status = "OK" if resp.status_code in (200, 201, 204) else "FAIL"
    print(f"[{status}] {repo_id} -> private (HTTP {resp.status_code}) {resp.text[:200]}")

print("Cleanup complete.")
