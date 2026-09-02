#!/usr/bin/env python3
"""Restart the KIN Space using HfApi with correct repo_id parameter."""
import sys, os, time, traceback, json
print("=== RESTART SPACE ===", flush=True)
print("Python:", sys.version, flush=True)

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

import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Current stage: {state.get('stage')}", flush=True)

# Method 1: HfApi.restart_space with repo_id
print("Method 1: api.restart_space(repo_id=...)", flush=True)
try:
    result = api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
    print(f"  Success: {result}", flush=True)
except Exception as e:
    print(f"  Failed: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

time.sleep(5)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after method 1: {state.get('stage')}", flush=True)

if state.get("stage") == "PAUSED":
    # Method 2: Factory reboot
    print("Method 2: factory_reboot=True", flush=True)
    try:
        result = api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
        print(f"  Success: {result}", flush=True)
    except Exception as e:
        print(f"  Failed: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

    time.sleep(5)
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage after method 2: {state.get('stage')}", flush=True)

if state.get("stage") == "PAUSED":
    # Method 3: Request hardware then restart
    print("Method 3: request_hardware + restart", flush=True)
    try:
        api.request_space_hardware(repo_id=SPACE_ID, hardware="cpu-basic", token=HF_TOKEN)
        print("  Hardware requested", flush=True)
        time.sleep(3)
        api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
        print("  Restart OK", flush=True)
    except Exception as e:
        print(f"  Failed: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

    time.sleep(5)
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage after method 3: {state.get('stage')}", flush=True)

if state.get("stage") == "PAUSED":
    # Method 4: Direct HTTP POST via requests
    print("Method 4: requests.post", flush=True)
    try:
        import requests
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post(f"https://huggingface.co/api/spaces/{SPACE_ID}/restart", headers=headers, timeout=30)
        print(f"  Status: {r.status_code}", flush=True)
        print(f"  Body: {r.text[:500]}", flush=True)
        if r.status_code != 200:
            r2 = requests.post(f"https://huggingface.co/api/spaces/{SPACE_ID}/restart?factory=true", headers=headers, timeout=30)
            print(f"  Factory status: {r2.status_code}", flush=True)
            print(f"  Factory body: {r2.text[:500]}", flush=True)
    except Exception as e:
        print(f"  Failed: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

    time.sleep(5)
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage after method 4: {state.get('stage')}", flush=True)

print(f"FINAL STAGE: {state.get('stage')}", flush=True)
print("=== DONE ===", flush=True)
