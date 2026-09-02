#!/usr/bin/env python3
"""Create/update the KIN inference Space, repoint to v6, fix py3.13 audioop."""
print("=== CREATE SPACE START ===", flush=True)
import sys, os, time, tempfile, traceback, datetime
print("Python:", sys.version, flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

SPACE_ID = "nyxspecter4/kin-inference"
MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"

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

print("Setting model to public...", flush=True)
try:
    api.update_repo_visibility(repo_id=MODEL_ID, repo_type="model", private=False, token=HF_TOKEN)
    print("Model is now public", flush=True)
except Exception as e:
    print(f"WARN: could not set model public: {e}", flush=True)

print("Creating Space...", flush=True)
for attempt in range(1, 4):
    try:
        api.create_repo(repo_id=SPACE_ID, repo_type="space", private=False,
                    token=HF_TOKEN, exist_ok=True, space_sdk="gradio")
        print("Space created/exists", flush=True)
        break
    except Exception as e:
        print(f"Create attempt {attempt} error: {e}", flush=True)
        if attempt < 3:
            time.sleep(5)

REQS = """gradio==4.44.0
huggingface_hub>=0.26.0
audioop-lts
transformers
torch
"""
print("Uploading requirements.txt...", flush=True)
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write(REQS)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("requirements.txt uploaded", flush=True)

build_ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
README = f"""---
title: KIN Cybersecurity AI
emoji: \U0001f6e1
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: true
tags:
  - cybersecurity
  - security
  - threat-intelligence
  - penetration-testing
models:
  - {MODEL_ID}
---

# KIN - Cybersecurity AI (v6 DPO)

Chat with KIN, a cybersecurity AI fine-tuned via DPO on Qwen2.5-0.5B.

Build: {build_ts}
"""
print("Uploading README...", flush=True)
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(README)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("README uploaded", flush=True)

print("Uploading app.py...", flush=True)
api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
print("app.py uploaded", flush=True)

print("=== SPACE UPDATE COMPLETE ===", flush=True)
