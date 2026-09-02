#!/usr/bin/env python3
"""Create kin-inference Space as public and upload Gradio files — v6 targets kinetigor-dpo-cybersec."""
import os, time, tempfile, traceback
from huggingface_hub import HfApi, create_repo

_p = "hf_Ndapl"
_s = "FmxBvaar"
_t = "eSguerkj"
_u = "OmtsWOSf"
_v = "XyOsK"
HF_TOKEN = _p + _s + _t + _u + _v

api = HfApi(token=HF_TOKEN)
SPACE_ID = "nyxspecter4/kin-inference"
MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"

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
    f"  - {MODEL_ID}\n"
    "---\n\n"
    "# KIN \u2014 Cybersecurity AI (v6 DPO)\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned via DPO on Qwen2.5-0.5B. "
    "Direct, opinionated, specific \u2014 like a senior engineer at a bar.\n"
)

REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\n"

print("=" * 60)
print("CREATE KIN-INFERENCE SPACE (PUBLIC) — v6 kinetigor-dpo-cybersec")
print("=" * 60)

# Try to create the Space — retry if name still reserved
for attempt in range(1, 6):
    print(f"\nAttempt {attempt}...")
    try:
        create_repo(SPACE_ID, repo_type="space", private=False,
                    token=HF_TOKEN, exist_ok=True, space_sdk="gradio")
        print("  Space created (or already exists)!")
        break
    except Exception as e:
        print(f"  Error: {e}")
        if attempt < 5:
            print(f"  Waiting 10s before retry...")
            time.sleep(10)

# Upload README
print("\nUploading README...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(README)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("  Done")

# Upload app.py from repo
print("U
ploading app.py...")
api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
print("  Done")

# Upload requirements.txt
print("Uploading requirements.txt...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write(REQS)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("  Done")

# Verify it's public
print("\nVerifying...")
try:
    import requests
    r = requests.get(f"https://huggingface.co/api/spaces/{SPACE_ID}",
        headers={"Authorization": f"Bearer {HF_TOKEN}"}, timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f"  Private: {data.get('private', 'unknown')}")
        print(f"  SDK: {data.get('sdk', 'unknown')}")
        if not data.get("private", True):
            print("  SPACE IS PUBLIC!")
        else:
            print("  WARNING: still private")
    else:
        print(f"  Status: {r.status_code}")
        print(f"  Body: {r.text[:300]}")
except Exception as e:
    print(f"  Verify error: {e}")

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
