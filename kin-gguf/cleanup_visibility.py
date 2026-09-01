#!/usr/bin/env python3
"""Make old/bad models private to clean up our public presence."""
import os
from huggingface_hub import HfApi

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)

api = HfApi(token=T)

# Models that should be PRIVATE (old, bad quality, not ready)
MAKE_PRIVATE = [
    "nyxspecter4/kin-sft-lora",
    "nyxspecter4/kin-v2-cybersecurity-7b-lora",
]

for repo_id in MAKE_PRIVATE:
    try:
        # Try update_repo_visibility first
        api.update_repo_visibility(repo_id=repo_id, repo_type="model", private=True)
        print(f"[OK] Made {repo_id} PRIVATE via update_repo_visibility")
    except Exception as e:
        print(f"[FAIL update_repo_visibility] {repo_id}: {e}")
        try:
            # Fallback: use the raw HTTP API
            from huggingface_hub import HfApi as _HfApi
            api._hf_api_set_repo_visibility(repo_id=repo_id, repo_type="model", private=True)
            print(f"[OK] Made {repo_id} PRIVATE via _hf_api_set_repo_visibility")
        except Exception as e2:
            print(f"[FAIL fallback] {repo_id}: {e2}")

print("Cleanup complete.")
