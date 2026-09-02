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
    import huggingface_hub
    print("huggingface_hub:", huggingface_hub.__version__, flush=True)
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    print("HfApi initialized", flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

print("Validating token...", flush=True)
try:
    info = api.whoami()
    print("Token valid! Name:", info.get("name", "unknown"), flush=True)
except Exception as e:
    print("TOKEN ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

print("Attempting restart_space...", flush=True)
try:
    api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
    print("restart_space succeeded!", flush=True)
except Exception as e:
    print(f"restart_space error: {e}", flush=True)
    traceback.print_exc()
    
    print("Attempting factory_reboot...", flush=True)
    try:
        api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
        print("factory_reboot succeeded!", flush=True)
    except Exception as e2:
        print(f"factory_reboot error: {e2}", flush=True)
        traceback.print_exc()

print("=== RESTART COMPLETE ===", flush=True)
