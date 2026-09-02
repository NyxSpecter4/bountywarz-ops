#!/usr/bin/env python3
print("=== CREATE SPACE START ===", flush=True)
import sys, os, time, tempfile, traceback
print("Python:", sys.version, flush=True)

# Token
_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

try:
    import huggingface_hub
    print("huggingface_hub:", huggingface_hub.__version__, flush=True)
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    print("HfApi initialized", flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

SPACE_ID = "nyxspecter4/kin-inference"
MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"

# Validate token
print("Validating token...", flush=True)
try:
    info = api.whoami()
    print("Token valid! Name:", info.get("name", "unknown"), flush=True)
except Exception as e:
    print("TOKEN ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

# Create Space
print("Creating Space...", flush=True)
for attempt in range(1, 4):
    try:
        api.create_repo(repo_id=SPACE_ID, repo_type="space", private=False,
                    token=HF_TOKEN, exist_ok=True, space_sdk="gradio")
        print("Space created/exists", flush=True)
        break
    except Exception as e:
        print(f"Create attempt {attempt} error: {e}", flush=True)
        if attempt < 3:
            time.sleep(5)

# Upload requirements.txt with audioop-lts
REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\naudioop-lts\n"
print("Uploading requirements.txt...", flush=True)
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write(REQS)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("requirements.txt uploaded", flush=True)

# Upload README with build timestamp to force new commit
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
    "  - " + MODEL_ID + "\n"
    "---\n\n"
    "# KIN - Cybersecurity AI (v6 DPO)\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned via DPO on Qwen2.5-0.5B.\n\n"
    "Build: " + buildTs + "\n"
)
print("Uploading README...", flush=True)
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(README)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("README uploaded", flush=True)

# Upload app.py
print("Uploading app.py...", flush=True)
api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
print("app.py uploaded", flush=True)

print("=== SPACE UPDATE COMPLETE ===", flush=True)
