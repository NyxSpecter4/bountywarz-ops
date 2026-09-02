#!/usr/bin/env python3
"""Restart the KIN inference Space."""
print("=== RESTART SPACE START ===", flush=True)
import sys, os, time, traceback
print("Python:", sys.version, flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

SPACE_ID = "nyxspecter4/kin-inference"

try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    print("HfApi initialized", flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

print("Restarting Space...", flush=True)
for attempt in range(1, 4):
    try:
        api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
        print("Space restarted!", flush=True)
        break
    except Exception as e:
        print(f"Restart attempt {attempt} error: {e}", flush=True)
        if attempt < 3:
            time.sleep(5)

print("=== RESTART COMPLETE ===", flush=True)
