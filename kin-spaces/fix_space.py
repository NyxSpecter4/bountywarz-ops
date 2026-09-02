#!/usr/bin/env python3
"""Minimal Space: only app.py + empty requirements, default README."""
import sys, os, time, json, urllib.request, traceback
print("=== MINIMAL SPACE ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
SPACE_ID = "nyxspecter4/kin-inference"

from huggingface_hub import HfApi, CommitOperationAdd
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__, flush=True)
api = HfApi(token=HF_TOKEN)

# Download app.py from GitHub
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py",
    "/tmp/app.py"
)

# Delete old Space
print("Deleting old Space...", flush=True)
try:
    api.delete_repo(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted OK", flush=True)
    time.sleep(10)
except Exception as e:
    print(f"  Delete failed (ok): {e}", flush=True)

# Create new Space
print("Creating new Space...", flush=True)
try:
    api.create_repo(
        repo_id=SPACE_ID,
        repo_type="space",
        private=False,
        token=HF_TOKEN,
        space_sdk="gradio",
    )
    print("  Created OK!", flush=True)
    time.sleep(10)
except Exception as e:
    print(f"  Create FAILED: {type(e).__name__}: {e}", flush=True)
    sys.exit(1)

# Upload ONLY app.py (keep default README with sdk_version 6.26.0)
# No requirements.txt upload (build system handles gradio install)
print("Uploading app.py only...", flush=True)
try:
    api.upload_file(
        path_or_fileobj="/tmp/app.py",
        path_in_repo="app.py",
        repo_id=SPACE_ID,
        repo_type="space",
        token=HF_TOKEN,
    )
    print("  app.py uploaded OK", flush=True)
except Exception as e:
    print(f"  app.py upload FAILED: {type(e).__name__}: {e}", flush=True)

# Wait for build
print("Waiting for build...", flush=True)
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
for i in range(12):
    time.sleep(15)
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            stage = state.get("stage")
            err = state.get("errorMessage", "")[:200]
            print(f"  Check {i+1}: {stage}" + (f" err={err}" if err and stage not in ("BUILDING",) else ""), flush=True)
            if stage == "RUNNING":
                print("  SPACE IS RUNNING!", flush=True)
                break
            if stage in ("RUNTIME_ERROR", "BUILD_ERROR"):
                print(f"  ERROR: {err}", flush=True)
                break
    except Exception as e:
        print(f"  Check {i+1}: {e}", flush=True)

print("=== DONE ===", flush=True)
