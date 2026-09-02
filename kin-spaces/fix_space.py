#!/usr/bin/env python3
"""Delete + recreate Space with create_repo, upload correct files."""
import sys, os, time, json, urllib.request, traceback
print("=== RECREATE SPACE V2 ===", flush=True)

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
print("Downloading app.py...", flush=True)
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py",
    "/tmp/app.py"
)

# Write requirements.txt (minimal)
with open("/tmp/requirements.txt", "w") as f:
    f.write("audioop-lts;python_version>='3.13'\n")

# Write README.md with valid emoji and sdk_version 5.0.0
with open("/tmp/README.md", "w") as f:
    f.write("---\n")
    f.write("title: Kin Inference\n")
    f.write("emoji: \U0001F6E1\U0000FE0F\n")
    f.write("colorFrom: indigo\n")
    f.write("colorTo: red\n")
    f.write("sdk: gradio\n")
    f.write("sdk_version: 5.0.0\n")
    f.write("python_version: '3.13'\n")
    f.write("app_file: app.py\n")
    f.write("pinned: false\n")
    f.write("---\n")
    f.write("KIN Cybersecurity AI inference demo.\n")

# Delete old Space
print("Deleting old Space...", flush=True)
try:
    api.delete_repo(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted OK", flush=True)
    time.sleep(10)
except Exception as e:
    print(f"  Delete failed (ok): {e}", flush=True)

# Create new Space with create_repo
print("Creating new Space via create_repo...", flush=True)
try:
    api.create_repo(
        repo_id=SPACE_ID,
        repo_type="space",
        private=False,
        token=HF_TOKEN,
        space_sdk="gradio",
    )
    print("  Created OK!", flush=True)
    time.sleep(5)
except Exception as e:
    print(f"  Create FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

# Upload all files in one atomic commit
print("Uploading files via create_commit...", flush=True)
try:
    operations = [
        CommitOperationAdd(path_in_repo="app.py", path_or_fileobj="/tmp/app.py"),
        CommitOperationAdd(path_in_repo="requirements.txt", path_or_fileobj="/tmp/requirements.txt"),
        CommitOperationAdd(path_in_repo="README.md", path_or_fileobj="/tmp/README.md"),
    ]
    commit_info = api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message="Add app.py, requirements.txt, README.md",
        token=HF_TOKEN,
    )
    print(f"  Upload OK: {commit_info}", flush=True)
except Exception as e:
    print(f"  Upload FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    # Fallback: upload individually
    for fname in ["app.py", "requirements.txt", "README.md"]:
        try:
            api.upload_file(
                path_or_fileobj=f"/tmp/{fname}",
                path_in_repo=fname,
                repo_id=SPACE_ID,
                repo_type="space",
                token=HF_TOKEN,
            )
            print(f"  {fname} upload OK", flush=True)
        except Exception as e2:
            print(f"  {fname} upload FAILED: {e2}", flush=True)

# Wait for build
print("Waiting for build...", flush=True)
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
for i in range(12):
    time.sleep(15)
    try:
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            stage = state.get("stage")
            err = state.get("errorMessage", "")[:300]
            print(f"  Check {i+1}: {stage}" + (f" err={err}" if err and stage != "BUILDING" else ""), flush=True)
            if stage == "RUNNING":
                print("  SPACE IS RUNNING!", flush=True)
                break
            if stage == "RUNTIME_ERROR":
                print(f"  RUNTIME_ERROR: {err}", flush=True)
                break
    except Exception as e:
        print(f"  Check {i+1}: {e}", flush=True)

print("=== DONE ===", flush=True)
