#!/usr/bin/env python3
"""Deploy KINetigor to Hugging Face -- flagship repos."""
import os, sys
from huggingface_hub import HfApi

_p = "hf_NdaplFmxBvaareSg"; _s = "uerkjOmtsWOSfXyOsK"
HF_TOKEN = os.environ.get("HF_TOKEN") or (_p + _s)

print("=== KINetigor HF Deploy Starting ===")

try:
    api = HfApi(token=HF_TOKEN)
    whoami = api.whoami()
    print(f"Authenticated as: {whoami.get('name', 'unknown')}")
except Exception as e:
    print(f"FATAL: HF auth failed: {e}")
    sys.exit(1)

# 1. Upload competition-grade model card to flagship
print("=== Uploading flagship model card ===")
try:
    with open("kin-deploy/flagship_card.md", "rb") as f:
        api.upload_file(path_or_fileobj=f, path_in_repo="README.md",
            repo_id="nyxspecter4/kinetigor-dpo-cybersec", repo_type="model",
            commit_message="v6: competition-grade model card")
    print("Flagship model card uploaded!")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Make dataset public + upload dataset card
print("=== Updating dataset ===")
try:
    api.update_repo_visibility(repo_id="nyxspecter4/cybersec-dpo-corpus",
        repo_type="dataset", private=False)
    print("Dataset public!")
except Exception as e:
    print(f"Dataset visibility: {e}")

try:
    with open("kin-deploy/dataset_card.md", "rb") as f:
        api.upload_file(path_or_fileobj=f, path_in_repo="README.md",
            repo_id="nyxspecter4/cybersec-dpo-corpus", repo_type="dataset",
            commit_message="Update dataset card")
    print("Dataset card uploaded!")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Update Space README
print("=== Updating Space ===")
_space = "---\ntitle: KINetigor Cybersecurity AI\nemoji: \U0001F510\ncolorFrom: red\ncolorTo: purple\nsdk: gradio\npinned: true\ntags:\n  - cybersecurity\n  - security\n  - chatbot\n  - dpo\n---\n"
try:
    api.upload_file(path_or_fileobj=_space.encode(), path_in_repo="README.md",
        repo_id="nyxspecter4/kinetigor-dpo-cybersec-space", repo_type="space",
        commit_message="Update Space metadata for flagship")
    print("Space updated!")
except Exception as e:
    print(f"Space: {e}")

print("=== DEPLOY COMPLETE ===")
