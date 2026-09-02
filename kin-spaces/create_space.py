#!/usr/bin/env python3
"""Upload app.py, requirements.txt, README.md to the KIN Space and restart it."""
print("=== CREATE/UPDATE SPACE START ===", flush=True)
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
    import huggingface_hub
    print("huggingface_hub version:", huggingface_hub.__version__, flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

api = HfApi(token=HF_TOKEN)

# === app.py content ===
APP_PY = '''import gradio as gr
from huggingface_hub import InferenceClient

MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"
client = InferenceClient(model=MODEL_ID, timeout=120)

SYSTEM_PROMPT = (
    "You are KIN \u2014 a sharp cybersecurity AI partner. Direct, opinionated, specific. "
    "Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. "
    "Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. "
    "Open with your take, not your title. No 'As a cybersecurity AI expert.' "
    "Name products: 'CrowdStrike Falcon' not 'use EDR'. 'Duo push MFA' not 'implement MFA'."
)


def respond(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": message}]
    try:
        response = client.chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[KIN hit an error \u2014 try again.] Error: {str(e)}"


demo = gr.ChatInterface(
    fn=respond,
    type="messages",
    title="KIN \u2014 Cybersecurity AI",
    description="Direct, opinionated cybersecurity advice. Like a senior engineer at a bar, not a textbook.",
    examples=[
        "How do I detect a foothold after a phishing attack?",
        "What went wrong with the MGM hack?",
        "Explain CVE-2024-3094 in plain English.",
        "What EDR should I actually buy?",
    ],
    theme=gr.themes.Soft(),
)

demo.launch()
'''

# === requirements.txt content ===
REQUIREMENTS_TXT = '''gradio>=5.0,<6.0
huggingface_hub>=0.26,<0.30
audioop-lts;python_version>="3.13"
'''

# === README.md content ===
README_MD = '''---
title: Kin Inference
emoji: 👁
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 5.0.0
python_version: '3.13'
app_file: app.py
pinned: false
---

# KIN \u2014 Cybersecurity AI

Inference demo for [KIN v6 DPO](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec), a cybersecurity AI fine-tuned via DPO on Qwen2.5-0.5B-Instruct.
'''

print("Files defined. Uploading to Space...", flush=True)

# Upload all 3 files in one commit
from huggingface_hub import CommitOperationAdd
operations = [
    CommitOperationAdd(path_in_repo="app.py", content=APP_PY),
    CommitOperationAdd(path_in_repo="requirements.txt", content=REQUIREMENTS_TXT),
    CommitOperationAdd(path_in_repo="README.md", content=README_MD),
]

try:
    commit_info = api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message="Add app.py, requirements.txt, README.md for KIN inference",
    )
    print(f"Upload succeeded! Commit: {commit_info}", flush=True)
except Exception as e:
    print(f"Upload failed: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

# Wait a moment for the commit to propagate
print("Waiting 5s for commit to propagate...", flush=True)
time.sleep(5)

# Check current state
import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after upload: {state.get('stage')}", flush=True)

# If still paused, restart
if state.get('stage') in ('PAUSED', 'RUNTIME_ERROR'):
    print("Space is not running, attempting restart...", flush=True)
    try:
        result = api.restart_space(space_id=SPACE_ID)
        print(f"restart_space result: {result}", flush=True)
    except Exception as e:
        print(f"restart_space failed: {e}", flush=True)
        traceback.print_exc()
        # Try factory reboot
        try:
            print("Trying factory reboot...", flush=True)
            result = api.restart_space(space_id=SPACE_ID, factory_reboot=True)
            print(f"factory reboot result: {result}", flush=True)
        except Exception as e2:
            print(f"factory reboot failed: {e2}", flush=True)
            traceback.print_exc()

# Final state check
time.sleep(5)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Final stage: {state.get('stage')}", flush=True)
    print(f"Hardware current: {state.get('hardware', {}).get('current')}", flush=True)

print("=== CREATE/UPDATE SPACE COMPLETE ===", flush=True)
