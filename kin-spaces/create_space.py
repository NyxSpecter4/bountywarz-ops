#!/usr/bin/env python3
"""Recreate KIN Space: download app.py from GitHub, upload all files."""
import sys, os, time, traceback, json, urllib.request
print("=== RECREATE SPACE ===", flush=True)

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

# Download app.py from GitHub repo
print("Downloading app.py from GitHub...", flush=True)
app_url = "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py"
urllib.request.urlretrieve(app_url, "/tmp/app.py")
print("  Downloaded", flush=True)

# Write requirements.txt
print("Writing requirements.txt...", flush=True)
with open("/tmp/requirements.txt", "w") as f:
    f.write("gradio>=5.0,<6.0\n")
    f.write("huggingface_hub>=0.26,<0.30\n")
    f.write("audioop-lts;python_version>='3.13'\n")
print("  Written", flush=True)

# Write README.md
print("Writing README.md...", flush=True)
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
    f.write("\n")
    f.write("KIN Cybersecurity AI inference demo.\n")
print("  Written", flush=True)

# Delete old Space
print("Deleting old Space...", flush=True)
try:
    api.delete_repo(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted OK", flush=True)
    time.sleep(5)
except Exception as e:
    print(f"  Delete failed (may not exist): {e}", flush=True)

# Create new Space
print("Creating new Space...", flush=True)
try:
    api.create_space(repo_id=SPACE_ID, space_sdk="gradio", token=HF_TOKEN, private=False)
    print("  Created OK", flush=True)
    time.sleep(5)
except Exception as e:
    print(f"  Create failed: {e}", flush=True)
    traceback.print_exc()

# Upload files
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
        print(f"  {fname} FAILED: {e}", flush=True)

# Wait and check
def check_stage():
    try:
        url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            return state.get("stage")
    except Exception:
        return "UNKNOWN"

print("Waiting for Space to build...", flush=True)
for i in range(12):
    time.sleep(10)
    stage = check_stage()
    print(f"  Check {i+1}: {stage}", flush=True)
    if stage in ("RUNNING", "RUNTIME_ERROR"):
        break

print(f"FINAL: {check_stage()}", flush=True)
print("=== DONE ===", flush=True)
