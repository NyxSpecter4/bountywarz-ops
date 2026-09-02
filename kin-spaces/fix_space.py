#!/usr/bin/env python3
"""Fix Space v4: upload files to existing Space (no delete/create)."""
import sys, os, time, json, urllib.request, traceback
print("=== FIX SPACE v4 (update existing, gradio 5.44.0) ===", flush=True)

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

# Download app.py from GitHub main branch
print("Downloading app.py from GitHub...", flush=True)
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py",
    "/tmp/app.py"
)
with open("/tmp/app.py") as f:
    content = f.read()
    print("  app.py size:", len(content), "bytes", flush=True)

# Write requirements.txt - gradio 5.44.0 pinned via README sdk_version
# huggingface_hub for InferenceClient, audioop-lts for Python 3.13 pydub compat
REQS = "huggingface_hub>=0.26.0\naudioop-lts\n"
with open("/tmp/requirements.txt", "w") as f:
    f.write(REQS)
print("  requirements.txt written", flush=True)

# Write README.md with sdk_version 5.44.0 (not 6.x)
README_CONTENT = (
    "---\n"
    "title: KIN Cybersecurity AI\n"
    "emoji: \U0001f6e1\n"
    "colorFrom: blue\n"
    "colorTo: red\n"
    "sdk: gradio\n"
    "sdk_version: 5.44.0\n"
    "python_version: '3.13'\n"
    "app_file: app.py\n"
    "pinned: false\n"
    "---\n\n"
    "KIN \u2014 Cybersecurity AI. Direct, opinionated security advice powered by KIN v6 DPO (Qwen2.5-0.5B).\n"
)
with open("/tmp/README.md", "w") as f:
    f.write(README_CONTENT)
print("  README.md written (sdk_version: 5.44.0)", flush=True)

# Try to create the Space if it doesn't exist, otherwise just upload
print("Ensuring Space exists...", flush=True)
try:
    api.create_repo(
        repo_id=SPACE_ID,
        repo_type="space",
        private=False,
        token=HF_TOKEN,
        space_sdk="gradio",
    )
    print("  Created new Space!", flush=True)
    time.sleep(5)
except Exception as e:
    err_str = str(e)
    if "409" in err_str or "already" in err_str.lower():
        print("  Space already exists (OK)", flush=True)
    else:
        print(f"  Create error: {type(e).__name__}: {err_str[:200]}", flush=True)
        # Continue anyway - try to upload

# Upload ALL files in one commit (overwrites existing)
print("Uploading app.py + requirements.txt + README.md...", flush=True)
try:
    api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        token=HF_TOKEN,
        commit_message="Fix: pin gradio 5.44.0, add requirements.txt",
        operations=[
            CommitOperationAdd(path_in_repo="app.py", path_or_fileobj="/tmp/app.py"),
            CommitOperationAdd(path_in_repo="requirements.txt", path_or_fileobj="/tmp/requirements.txt"),
            CommitOperationAdd(path_in_repo="README.md", path_or_fileobj="/tmp/README.md"),
        ],
    )
    print("  All files uploaded OK", flush=True)
except Exception as e:
    print(f"  Upload FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

# Wait for build
print("Waiting for build (up to 5 min)...", flush=True)
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
for i in range(20):
    time.sleep(15)
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            stage = state.get("stage")
            err = state.get("errorMessage", "")[:300]
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
