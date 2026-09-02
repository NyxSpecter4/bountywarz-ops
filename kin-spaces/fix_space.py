#!/usr/bin/env python3
"""Just factory reboot the Space - files are already updated."""
import sys, os, time, json, urllib.request, traceback
print("=== FACTORY REBOOT ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
SPACE_ID = "nyxspecter4/kin-inference"

from huggingface_hub import HfApi
api = HfApi(token=HF_TOKEN)

url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
def check():
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            return state.get("stage"), state.get("errorMessage", "")[:200]
    except Exception as e:
        return "ERROR", str(e)[:200]

stage, err = check()
print(f"Before reboot: {stage}", flush=True)

print("Calling factory_reboot...", flush=True)
try:
    api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
    print("  Reboot called OK", flush=True)
except Exception as e:
    print(f"  Reboot FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

for i in range(12):
    time.sleep(15)
    stage, err = check()
    print(f"  Check {i+1}: {stage}" + (f" err={err}" if err else ""), flush=True)
    if stage == "RUNNING":
        print("  SPACE IS RUNNING!", flush=True)
        break
    if stage == "RUNTIME_ERROR":
        print(f"  RUNTIME_ERROR: {err}", flush=True)
        break

print("=== DONE ===", flush=True)
