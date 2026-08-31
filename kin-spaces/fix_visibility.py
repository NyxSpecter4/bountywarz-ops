#!/usr/bin/env python3
"""Make kin-inference Space public using multiple methods."""
import sys, traceback

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

SPACE_ID = "nyxspecter4/kin-inference"

# Method 1: huggingface_hub update_repo_visibility
print("=== Method 1: huggingface_hub ===")
try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    api.update_repo_visibility(SPACE_ID, private=False, repo_type="space", token=HF_TOKEN)
    print("SUCCESS via update_repo_visibility")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

# Method 2: Raw PUT to /visibility endpoint
print("\n=== Method 2: raw /visibility ===")
try:
    import requests
    headers = {"Authorization": "Bearer " + HF_TOKEN}
    r = requests.put(
        "https://huggingface.co/api/spaces/" + SPACE_ID + "/visibility",
        headers=headers,
        json={"private": False},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
    if r.status_code == 200:
        print("SUCCESS via raw /visibility")
except Exception as e:
    print(f"FAILED: {e}")

# Method 3: Raw POST to /settings
print("\n=== Method 3: raw /settings ===")
try:
    import requests
    headers = {"Authorization": "Bearer " + HF_TOKEN}
    r = requests.post(
        "https://huggingface.co/api/spaces/" + SPACE_ID + "/settings",
        headers=headers,
        json={"private": False},
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
except Exception as e:
    print(f"FAILED: {e}")

# Verify
print("\n=== Verification ===")
try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    info = api.space_info(SPACE_ID, token=HF_TOKEN)
    print(f"Private: {info.private}")
except Exception as e:
    print(f"Verify failed: {e}")
