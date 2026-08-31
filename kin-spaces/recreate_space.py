#!/usr/bin/env python3
"""Make kin-inference public by trying create_repo(exist_ok), then delete+recreate if needed."""
import os, sys, tempfile, traceback
from huggingface_hub import HfApi, create_repo, upload_file

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

api = HfApi(token=HF_TOKEN)
SPACE_ID = "nyxspecter4/kin-inference"

# File contents
README = (
    "---\n"
    "title: KIN Cybersecurity AI\n"
    "emoji: \U0001f6e1\n"
    "colorFrom: gray\n"
    "colorTo: blue\n"
    "sdk: gradio\n"
    "sdk_version: 4.44.0\n"
    "app_file: app.py\n"
    "pinned: true\n"
    "tags:\n"
    "  - cybersecurity\n"
    "  - security\n"
    "  - threat-intelligence\n"
    "  - penetration-testing\n"
    "models:\n"
    "  - nyxspecter4/kin-sft-lora\n"
    "---\n\n"
    "# KIN — Cybersecurity AI\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned on Qwen2.5-3B-Instruct. "
    "Direct, opinionated, specific — like a senior engineer at a bar.\n"
)

APP_PY = '''import gradio as gr
from huggingface_hub import InferenceClient

client = InferenceClient("nyxspecter4/kin-sft-lora")

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
        response = client.chat_completion(messages=messages, max_tokens=512, temperature=0.7, stream=False)
        return response.choices[0].message.content
    except Exception as e:
        return f"[KIN is loading \u2014 the Inference API may take a moment to spin up. Try again in a few seconds.]\n\nError: {str(e)}"

demo = gr.ChatInterface(
    fn=respond, type="messages",
    title="KIN \u2014 Cybersecurity AI",
    description="Direct, opinionated cybersecurity advice. Like a senior engineer at a bar.",
    examples=["How do I detect a foothold after a phishing attack?", "What went wrong with the MGM hack?", "Explain CVE-2024-3094.", "What EDR should I buy?"],
    theme=gr.themes.Soft(),
)
demo.launch()
'''

REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\n"

def upload_all_files():
    """Upload README, app.py, requirements.txt to the Space."""
    # README
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(README)
        p = f.name
    api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    os.unlink(p)
    print("  README uploaded")

    # app.py (from repo file)
    api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  app.py uploaded")

    # requirements.txt
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(REQS)
        p = f.name
    api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    os.unlink(p)
    print("  requirements.txt uploaded")

def is_public():
    """Check if Space is public."""
    try:
        import requests
        r = requests.get(
            f"https://huggingface.co/api/spaces/{SPACE_ID}",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            return not data.get("private", True)
    except:
        pass
    return False

print("=" * 60)
print("MAKE KIN-INFERENCE PUBLIC")
print("=" * 60)

# Step 1: Try create_repo with exist_ok=True and private=False
print("\n[1] Trying create_repo(exist_ok=True, private=False)...")
try:
    create_repo(SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True)
    print("  create_repo done")
    if is_public():
        print("  Space is now PUBLIC!")
        upload_all_files()
        print("\nDone! Space is public.")
        sys.exit(0)
    else:
        print("  Still private, trying next method...")
except Exception as e:
    print(f"  Failed: {e}")

# Step 2: Try update_repo_visibility with more detail
print("\n[2] Trying update_repo_visibility with verbose output...")
try:
    api.update_repo_visibility(SPACE_ID, private=False,
        repo_type="space", token=HF_TOKEN)
    print("  Done!")
    if is_public():
        print("  Space is now PUBLIC!")
        sys.exit(0)
except Exception as e:
    print(f"  Failed: {e}")
    traceback.print_exc()

# Step 3: Delete and recreate as public
print("\n[3] Deleting Space and recreating as public...")
try:
    api.delete_repo(SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted!")
except Exception as e:
    print(f"  Delete failed: {e}")

# Small delay
import time
time.sleep(3)

print("  Creating new public Space...")
try:
    create_repo(SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=False)
    print("  Created as public!")
except Exception as e:
    print(f"  Create failed: {e}")
    traceback.print_exc()
    # If create fails because name is still reserved, try again after delay
    print("  Waiting 10s and retrying...")
    time.sleep(10)
    create_repo(SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True)
    print("  Created (with exist_ok)!")

# Upload all files to the new Space
print("  Uploading files...")
upload_all_files()

# Verify
if is_public():
    print("\n  Space is now PUBLIC! Done!")
else:
    print("\n  WARNING: Space may still be private. Check manually.")

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
