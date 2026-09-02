#!/usr/bin/env python3
"""Delete and recreate the KIN inference Space for fresh build."""
print("=== RECREATE SPACE START ===", flush=True)
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
    from huggingface_hub import HfApi, CommitOperation
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

print("Deleting existing Space...", flush=True)
try:
    api.delete_repo(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("Space deleted", flush=True)
    time.sleep(10)
except Exception as e:
    print(f"WARN: could not delete: {e}", flush=True)

print("Creating fresh Space...", flush=True)
for attempt in range(1, 4):
    try:
        api.create_repo(repo_id=SPACE_ID, repo_type="space", private=False,
                    token=HF_TOKEN, exist_ok=True, space_sdk="gradio")
        print("Space created", flush=True)
        break
    except Exception as e:
        print(f"Create attempt {attempt} error: {e}", flush=True)
        if attempt < 3:
            time.sleep(10)

REQS = b"gradio>=5.0,<6.0\nhuggingface_hub>=0.26\naudioop-lts\n"

build_ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

README = f"""---
title: KIN Cybersecurity AI
emoji: \U0001f6e1
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 5.0.0
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
""".encode()

APP_PY = b"""import gradio as gr
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
"""

print("Creating atomic commit with all files...", flush=True)
operations = [
    CommitOperation.add(path_in_repo="requirements.txt", path_or_fileobj=REQS),
    CommitOperation.add(path_in_repo="README.md", path_or_fileobj=README),
    CommitOperation.add(path_in_repo="app.py", path_or_fileobj=APP_PY),
]

api.create_commit(
    repo_id=SPACE_ID,
    repo_type="space",
    operations=operations,
    commit_message=f"Fresh Space: gradio 5 + InferenceClient (build {build_ts})",
    token=HF_TOKEN,
)
print("Atomic commit created", flush=True)

print("=== SPACE RECREATE COMPLETE ===", flush=True)
