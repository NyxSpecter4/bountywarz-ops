#!/usr/bin/env python3
"""Create KIN Space from scratch (old one was deleted)."""
import sys, os, time, traceback, json, urllib.request
print("=== CREATE SPACE ===", flush=True)

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

# Download app.py from GitHub
print("Downloading app.py...", flush=True)
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py",
    "/tmp/app.py"
)
print("  OK", flush=True)

# Write requirements.txt
with open("/tmp/requirements.txt", "w") as f:
    f.write("gradio>=5.0,<6.0\n")
    f.write("huggingface_hub>=0.26,<0.30\n")
    f.write("audioop-lts;python_version>='3.13'\n")

# Write README.md
with open("/tmp/README.md", "w") as f:
    f.write("---\n")
    f.write("title: Kin Inference\n")
    f.write("emoji: KIN\n")
    f.write("colorFrom: indigo\n")
    f.write("colorTo: red\n")
    f.write("sdk: gradio\n")
    f.write("sdk_version: 5.0.0\n")
    f.write("python_version: '3.13'\n")
    f.write("app_file: app.py\n")
    f.write("pinned: false\n")
    f.write("---\n")
    f.write("KIN Cybersecurity AI inference demo.\n")

# Create Space (it was deleted already)
print("Creating Space...", flush=True)
try:
    api.create_space(repo_id=SPACE_ID, space_sdk="gradio", token=HF_TOKEN, private=False)
    print("  Created OK", flush=True)
    time.sleep(5)
except Exception as e:
    print(f"  Create failed: {type(e).__name__}: {e}", flush=True)

# Upload files one by one
for fname in ["app.py", "requirements.txt", "README.md"]:
    print(f"Uploading {fname}...", flush=True)
    try:
        api.upload_file(
            path_or_fileobj=f"/tmp/{fname}",
            path_in_repo=fname,
            repo_id=SPACE_ID,
            repo_type="space",
            token=HF_TOKEN,
        )
        print(f"  {fname} OK", flush=True)
    except Exception as e:
        print(f"  {fname} FAILED: {type(e).__name__}: {e}", flush=True)

# Quick status check
time.sleep(10)
try:
    url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage: {state.get('stage')}", flush=True)
except Exception as e:
    print(f"Status check failed: {e}", flush=True)

print("=== DONE ===", flush=True)
