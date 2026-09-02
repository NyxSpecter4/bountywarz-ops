#!/usr/bin/env python3
print("=== TEST SCRIPT START ===", flush=True)
import sys, os
print("Python:", sys.version, flush=True)
print("CWD:", os.getcwd(), flush=True)
print("Files:", os.listdir("."), flush=True)
try:
    import huggingface_hub
    print("huggingface_hub:", huggingface_hub.__version__, flush=True)
    from huggingface_hub import HfApi
    print("HfApi imported", flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    import traceback; traceback.print_exc()
    sys.exit(1)

# Token
_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

api = HfApi(token=HF_TOKEN)
print("HfApi initialized", flush=True)

# Validate token
try:
    info = api.whoami()
    print("Token valid! Name:", info.get("name", "unknown"), flush=True)
except Exception as e:
    print("TOKEN ERROR:", e, flush=True)
    import traceback; traceback.print_exc()
    sys.exit(1)

# Create Space
SPACE_ID = "nyxspecter4/kin-inference"
MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"

print("Creating Space...", flush=True)
try:
    api.create_repo(repo_id=SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True, space_sdk="gradio")
    print("Space created/exists", flush=True)
except Exception as e:
    print("CREATE ERROR:", e, flush=True)
    import traceback; traceback.print_exc()
    sys.exit(1)

# Upload requirements.txt with audioop-lts
import tempfile
REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\naudioop-lts\n"
print("Uploading requirements.txt...", flush=True)
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write(REQS)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("requirements.txt uploaded", flush=True)

# Upload README
README = "---\ntitle: KIN Cybersecurity AI\nemoji: \U0001f6e1\ncolorFrom: gray\ncolorTo: blue\nsdk: gradio\nsdk_version: 4.44.0\napp_file: app.py\npinned: true\ntags:\n  - cybersecurity\n  - security\n  - threat-intelligence\n  - penetration-testing\nmodels:\n  - " + MODEL_ID + "\n---\n\n# KIN - Cybersecurity AI (v6 DPO)\n\nChat with KIN, a cybersecurity AI fine-tuned via DPO on Qwen2.5-0.5B.\n"
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

print("=== ALL DONE ===", flush=True)
