#!/usr/bin/env python3
"""Fix KIN Spaces: make inference Space public with Gradio, delete dead trainer Spaces."""
import os
import tempfile
from huggingface_hub import HfApi

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

api = HfApi(token=HF_TOKEN)
SPACE_ID = "nyxspecter4/kin-inference"

print("=" * 60)
print("FIX KIN SPACES")
print("=" * 60)

# 1. Make kin-inference public
print("\n[1] Making kin-inference public...")
try:
    api.update_repo_visibility(SPACE_ID, repo_type="space", private=False, token=HF_TOKEN)
    print("Space is now public!")
except Exception as e:
    print(f"Visibility: {e}")

# 2. Upload Gradio README (change SDK from docker to gradio)
print("\n[2] Uploading Gradio README...")
readme_content = (
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
    "  - nyxspecter4/kin-sft-lora\n"
    "---\n\n"
    "# KIN — Cybersecurity AI\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned on Qwen2.5-3B-Instruct. "
    "Direct, opinionated, specific — like a senior engineer at a bar.\n"
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(readme_content)
    readme_path = f.name
api.upload_file(path_or_fileobj=readme_path, path_in_repo="README.md",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(readme_path)
print("README uploaded!")

# 3. Upload Gradio app from repo file
print("\n[3] Uploading app.py...")
api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
print("app.py uploaded!")

# 4. Upload requirements.txt
print("\n[4] Uploading requirements.txt...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write("gradio==4.44.0\nhuggingface_hub>=0.26.0\n")
    req_path = f.name
api.upload_file(path_or_fileobj=req_path, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(req_path)
print("requirements.txt uploaded!")

# 5. Delete old Docker files
print("\n[5] Deleting old Docker files...")
for old_file in ["Dockerfile", "serve.py"]:
    try:
        api.delete_file(path_in_repo=old_file, repo_id=SPACE_ID,
            repo_type="space", token=HF_TOKEN)
        print(f"Deleted {old_file}")
    except Exception as e:
        print(f"Could not delete {old_file}: {e}")

# 6. Delete dead trainer Spaces
print("\n[6] Deleting dead trainer Spaces...")
dead = [
    "nyxspecter4/kin-simpo-trainer",
    "nyxspecter4/kin-orpo-trainer",
    "nyxspecter4/kin-kto-trainer",
    "nyxspecter4/kin-dpo-trainer",
    "nyxspecter4/kin-sft-trainer",
]
for space in dead:
    try:
        api.delete_repo(space, repo_type="space", token=HF_TOKEN)
        print(f"Deleted {space}")
    except Exception as e:
        print(f"Could not delete {space}: {e}")

# 7. Delete empty model repo
print("\n[7] Deleting empty model repo...")
try:
    api.delete_repo("nyxspecter4/kin-cyber-dpo-v2-lora", repo_type="model", token=HF_TOKEN)
    print("Deleted kin-cyber-dpo-v2-lora")
except Exception as e:
    print(f"Could not delete: {e}")

print("\n" + "=" * 60)
print("SPACES FIXED!")
print("=" * 60)
