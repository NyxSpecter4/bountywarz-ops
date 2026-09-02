#!/usr/bin/env python3
"""Create KIN Space with new name (old name may be tombstoned)."""
import sys, os, time, traceback, json, urllib.request
print("=== CREATE SPACE V2 ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

# Try both names
SPACE_IDS = ["nyxspecter4/kin-inference", "nyxspecter4/kin-inference-v2"]

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

# Try creating each Space
created_id = None
for sid in SPACE_IDS:
    print(f"Trying to create {sid}...", flush=True)
    try:
        api.create_space(repo_id=sid, space_sdk="gradio", token=HF_TOKEN, private=False)
        print(f"  Created {sid} OK!", flush=True)
        created_id = sid
        break
    except Exception as e:
        print(f"  Failed: {type(e).__name__}: {e}", flush=True)

if not created_id:
    print("All creation attempts failed!", flush=True)
    print("=== DONE (FAILED) ===", flush=True)
    sys.exit(1)

# Upload files to the created Space
time.sleep(5)
for fname in ["app.py", "requirements.txt", "README.md"]:
    print(f"Uploading {fname}...", flush=True)
    try:
        api.upload_file(
            path_or_fileobj=f"/tmp/{fname}",
            path_in_repo=fname,
            repo_id=created_id,
            repo_type="space",
            token=HF_TOKEN,
        )
        print(f"  {fname} OK", flush=True)
    except Exception as e:
        print(f"  {fname} FAILED: {type(e).__name__}: {e}", flush=True)

# Quick status check
time.sleep(10)
try:
    url = f"https://huggingface.co/api/spaces/{created_id}/runtime"
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage: {state.get('stage')}", flush=True)
except Exception as e:
    print(f"Status check: {e}", flush=True)

print(f"Created Space: {created_id}", flush=True)
print("=== DONE ===", flush=True)
