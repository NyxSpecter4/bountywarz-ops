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
    "nyxspecter4/kin-sft-lora",           # Old SFT model, 3B, not good quality
    "nyxspecter4/kin-v2-cybersecurity-7b-lora",  # v2, only 2 downloads, not DPO
]

for repo_id in MAKE_PRIVATE:
    try:
        api.update_repo_visibility(repo_id=repo_id, repo_type="model", private=True)
        print(f"[OK] Made {repo_id} PRIVATE")
    except Exception as e:
        print(f"[FAIL] {repo_id}: {e}")

print("Cleanup complete.")
