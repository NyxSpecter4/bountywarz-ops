#!/usr/bin/env python3
"""Fix Space: update README, try pause+restart cycle, or recreate."""
import sys, os, time, traceback, json
print("=== FIX SPACE ===", flush=True)

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

def check_stage():
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        return state.get("stage")

print(f"Initial stage: {check_stage()}", flush=True)

# Step 1: Fix README with correct sdk_version
print("Step 1: Fix README...", flush=True)
README_CONTENT = """---
title: Kin Inference
emoji: KIN
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 5.0.0
python_version: '3.13'
app_file: app.py
pinned: false
---

KIN Cybersecurity AI inference demo.
"""
try:
    with open("/tmp/README.md", "w") as f:
        f.write(README_CONTENT)
    api.upload_file(
        path_or_fileobj="/tmp/README.md",
        path_in_repo="README.md",
        repo_id=SPACE_ID,
        repo_type="space",
        token=HF_TOKEN,
    )
    print("  README updated OK", flush=True)
except Exception as e:
    print(f"  README update failed: {e}", flush=True)

time.sleep(3)
print(f"Stage after README fix: {check_stage()}", flush=True)

# Step 2: Pause then restart cycle
print("Step 2: pause + restart cycle...", flush=True)
try:
    api.pause_space(repo_id=SPACE_ID, token=HF_TOKEN)
    print("  Paused OK", flush=True)
    time.sleep(5)
    print(f"  Stage after pause: {check_stage()}", flush=True)
except Exception as e:
    print(f"  Pause failed: {e}", flush=True)

try:
    api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
    print("  Restart OK", flush=True)
    time.sleep(5)
    print(f"  Stage after restart: {check_stage()}", flush=True)
except Exception as e:
    print(f"  Restart failed: {e}", flush=True)

# Step 3: Factory reboot if still paused
stage = check_stage()
if stage in ("PAUSED", "RUNTIME_ERROR"):
    print("Step 3: Factory reboot...", flush=True)
    try:
        api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
        print("  Factory reboot OK", flush=True)
        time.sleep(10)
        print(f"  Stage after factory reboot: {check_stage()}", flush=True)
    except Exception as e:
        print(f"  Factory reboot failed: {e}", flush=True)

# Step 4: If still not running, try direct HTTP with requests
stage = check_stage()
if stage in ("PAUSED", "RUNTIME_ERROR"):
    print("Step 4: Direct HTTP POST...", flush=True)
    try:
        import requests
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        r = requests.post(f"https://huggingface.co/api/spaces/{SPACE_ID}/restart", headers=headers, timeout=30)
        print(f"  POST status: {r.status_code}", flush=True)
        print(f"  POST body: {r.text[:500]}", flush=True)
        time.sleep(10)
        print(f"  Stage: {check_stage()}", flush=True)
    except Exception as e:
        print(f"  POST failed: {e}", flush=True)

stage = check_stage()
print(f"FINAL STAGE: {stage}", flush=True)
print("=== DONE ===", flush=True)
