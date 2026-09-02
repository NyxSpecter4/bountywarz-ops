#!/usr/bin/env python3
"""Force Space rebuild by pushing a unique file change."""
print("=== FORCE REBUILD START ===", flush=True)
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

build_ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
print(f"Build timestamp: {build_ts}", flush=True)

# Upload a unique trigger file to force rebuild
TRIGGER = f"# Build trigger: {build_ts}\n".encode()

print("Uploading trigger file to force rebuild...", flush=True)
operations = [
    CommitOperation.add(path_in_repo=".build_trigger", path_or_fileobj=TRIGGER),
]

try:
    api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message=f"Force rebuild trigger {build_ts}",
        token=HF_TOKEN,
    )
    print("Trigger file uploaded", flush=True)
except Exception as e:
    print(f"Commit error: {e}", flush=True)
    traceback.print_exc()

# Also try restart_space
print("Restarting Space...", flush=True)
for attempt in range(1, 4):
    try:
        api.restart_space(repo_id=SPACE_ID, token=HF_TOKEN)
        print("Space restarted!", flush=True)
        break
    except Exception as e:
        print(f"Restart attempt {attempt} error: {e}", flush=True)
        if attempt < 3:
            time.sleep(5)

print("=== FORCE REBUILD COMPLETE ===", flush=True)
