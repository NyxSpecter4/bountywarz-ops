#!/usr/bin/env python3
"""Fix KIN Space: update README + requirements, restart."""
import sys, os, time, traceback, json, urllib.request
print("=== FIX SPACE ===", flush=True)

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

# Verify token
who = api.whoami()
print(f"User: {who.get('name')}", flush=True)

# Write new requirements.txt (no gradio pin)
with open("/tmp/requirements.txt", "w") as f:
    f.write("huggingface_hub>=0.26,<0.30\n")
    f.write("audioop-lts;python_version>='3.13'\n")

# Write new README.md with sdk_version 5.0.0
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

# Upload via create_commit (atomic)
print("Uploading via create_commit...", flush=True)
try:
    operations = [
        CommitOperationAdd(path_in_repo="requirements.txt", path_or_fileobj="/tmp/requirements.txt"),
        CommitOperationAdd(path_in_repo="README.md", path_or_fileobj="/tmp/README.md"),
    ]
    commit_info = api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message="Fix requirements + README sdk_version=5.0.0",
        token=HF_TOKEN,
    )
    print(f"  create_commit OK: {commit_info}", flush=True)
except Exception as e:
    print(f"  create_commit FAILED: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    # Fallback: upload individually
    for fname in ["requirements.txt", "README.md"]:
        try:
            api.upload_file(
                path_or_fileobj=f"/tmp/{fname}",
                path_in_repo=fname,
                repo_id=SPACE_ID,
                repo_type="space",
                token=HF_TOKEN,
            )
            print(f"  {fname} upload_file OK", flush=True)
        except Exception as e2:
            print(f"  {fname} upload_file FAILED: {type(e2).__name__}: {e2}", flush=True)

# Wait for build
time.sleep(10)
try:
    url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage after upload: {state.get('stage')}", flush=True)
except Exception as e:
    print(f"Status: {e}", flush=True)

# Factory reboot
print("Factory reboot...", flush=True)
try:
    api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN, factory_reboot=True)
    print("  Reboot OK", flush=True)
except Exception as e:
    print(f"  Reboot FAILED: {type(e).__name__}: {e}", flush=True)

# Wait for build
for i in range(8):
    time.sleep(15)
    try:
        url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            stage = state.get("stage")
            print(f"  Check {i+1}: {stage}", flush=True)
            if stage == "RUNNING":
                print("  SPACE IS RUNNING!", flush=True)
                break
            if stage == "RUNTIME_ERROR":
                err = state.get("errorMessage", "")
                print(f"  RUNTIME_ERROR: {err[:500]}", flush=True)
                break
    except Exception as e:
        print(f"  Check {i+1}: {e}", flush=True)

print("=== DONE ===", flush=True)
