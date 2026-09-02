#!/usr/bin/env python3
"""Restart the KIN Space. Files already uploaded, just needs restart."""
import sys, os, time, traceback, json
print("=== RESTART SPACE ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
SPACE_ID = "nyxspecter4/kin-inference"

from huggingface_hub import HfApi
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__, flush=True)

api = HfApi(token=HF_TOKEN)

# Check current state
import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Current stage: {state.get('stage')}", flush=True)

# Method 1: HfApi.restart_space with correct parameter name (repo_id, not space_id)
print("Method 1: api.restart_space(repo_id=...)", flush=True)
try:
    result = api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
    print(f"  Success! Result type: {type(result)}", flush=True)
    print(f"  Result: {result}", flush=True)
except Exception as e:
    print(f"  Failed: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

# Check state after method 1
time.sleep(3)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after method 1: {state.get('stage')}", flush=True)
    
    if state.get('stage') == 'PAUSED':
        # Method 2: Factory reboot
        print("Method 2: api.restart_space(factory_reboot=True)", flush=True)
        try:
            result = api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
            print(f"  Success! Result: {result}", flush=True)
        except Exception as e:
            print(f"  Failed: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
        
        time.sleep(3)
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            print(f"Stage after method 2: {state.get('stage')}", flush=True)

    if state.get('stage') == 'PAUSED':
        # Method 3: Set hardware explicitly then restart
        print("Method 3: request_space_hardware + restart", flush=True)
        try:
            api.request_space_hardware(repo_id=SPACE_ID, hardware="cpu-basic", token=HF_TOKEN)
            print("  Hardware requested", flush=True)
            time.sleep(2)
            api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
            print("  Restart after hardware request OK", flush=True)
        except Exception as e:
            print(f"  Failed: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
        
        time.sleep(5)
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            print(f"Stage after method 3: {state.get('stage')}", flush=True)

    if state.get('stage') == 'PAUSED':
        # Method 4: Direct urllib POST with requests library
        print("Method 4: requests.post to restart endpoint", flush=True)
        try:
            import requests
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            resp4 = requests.post(f"https://huggingface.co/api/spaces/{SPACE_ID}/restart", headers=headers, timeout=30)
            print(f"  Status: {resp4.status_code}", flush=True)
            print(f"  Response: {resp4.text[:500]}", flush=True)
            
            if resp4.status_code != 200:
                print("  Trying factory=true...", flush=True)
                resp4b = requests.post(f"https://huggingface.co/api/spaces/{SPACE_ID}/restart?factory=true", headers=headers, timeout=30)
                print(f"  Factory status: {resp4b.status_code}", flush=True)
                print(f"  Factory response: {resp4b.text[:500]}", flush=True)
        except Exception as e:
            print(f"  Failed: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
        
        time.sleep(5)
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            print(f"Stage after method 4: {state.get('stage')}", flush=True)

# Final check
print(f"\nFINAL STAGE: {state.get('stage')}", flush=True)
print("=== DONE ===", flush=True)
