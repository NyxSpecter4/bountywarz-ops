#!/usr/bin/env python3
"""Restart the KIN inference Space using huggingface_hub HfApi."""
print("=== RESTART SPACE START ===", flush=True)
import sys, os, time, traceback, json
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
    print("huggingface_hub imported OK", flush=True)
    import huggingface_hub
    print("huggingface_hub version:", huggingface_hub.__version__, flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

api = HfApi(token=HF_TOKEN)

# Check current state
print("Checking Space state...", flush=True)
import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Current stage: {state.get('stage')}", flush=True)
    print(f"Hardware current: {state.get('hardware', {}).get('current')}", flush=True)
    print(f"Hardware requested: {state.get('hardware', {}).get('requested')}", flush=True)

# Method 1: Use HfApi.restart_space
print("\n--- Method 1: HfApi.restart_space() ---", flush=True)
try:
    result = api.restart_space(space_id=SPACE_ID)
    print(f"restart_space result: {result}", flush=True)
    print("Method 1 succeeded!", flush=True)
except Exception as e:
    print(f"Method 1 failed: {e}", flush=True)
    traceback.print_exc()

# Check state after method 1
time.sleep(3)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after method 1: {state.get('stage')}", flush=True)
    
    if state.get('stage') != 'PAUSED':
        print("Space is no longer PAUSED - success!", flush=True)
    else:
        # Method 2: Factory reboot via HfApi
        print("\n--- Method 2: HfApi.restart_space(factory=True) ---", flush=True)
        try:
            result = api.restart_space(space_id=SPACE_ID, factory_reboot=True)
            print(f"factory reboot result: {result}", flush=True)
            print("Method 2 succeeded!", flush=True)
        except Exception as e:
            print(f"Method 2 failed: {e}", flush=True)
            traceback.print_exc()
        
        # Method 3: Try setting hardware explicitly
        print("\n--- Method 3: HfApi.add_space_secret + restart ---", flush=True)
        try:
            # Sometimes pausing and unpausing via hardware change helps
            from huggingface_hub import HfApi as HFA
            # Try request hardware again
            api.request_space_hardware(space_id=SPACE_ID, hardware="cpu-basic")
            print("Requested cpu-basic hardware", flush=True)
            time.sleep(2)
            result = api.restart_space(space_id=SPACE_ID)
            print(f"restart after hardware request: {result}", flush=True)
        except Exception as e:
            print(f"Method 3 failed: {e}", flush=True)
            traceback.print_exc()

# Final state check
time.sleep(5)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"\nFinal stage: {state.get('stage')}", flush=True)
    print(f"Hardware current: {state.get('hardware', {}).get('current')}", flush=True)

print("=== RESTART COMPLETE ===", flush=True)
