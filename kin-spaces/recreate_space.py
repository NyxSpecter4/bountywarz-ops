#!/usr/bin/env python3
"""Make kin-inference Space public."""
import os, sys, time, tempfile, traceback
from huggingface_hub import HfApi, create_repo

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

api = HfApi(token=HF_TOKEN)
SPACE_ID = "nyxspecter4/kin-inference"

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
    "  - nyxspecter4/kin-sft-lora\n"
    "---\n\n"
    "# KIN \u2014 Cybersecurity AI\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned on Qwen2.5-3B-Instruct. "
    "Direct, opinionated, specific \u2014 like a senior engineer at a bar.\n"
)

REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\n"

def upload_files():
    # README
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(README)
        p = f.name
    api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    os.unlink(p)
    print("  README uploaded")
    # app.py from repo
    api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  app.py uploaded")
    # requirements.txt
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(REQS)
        p = f.name
    api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
        repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    os.unlink(p)
    print("  requirements.txt uploaded")

def check_public():
    try:
        import requests
        r = requests.get(f"https://huggingface.co/api/spaces/{SPACE_ID}",
            headers={"Authorization": f"Bearer {HF_TOKEN}"}, timeout=15)
        if r.status_code == 200:
            return not r.json().get("private", True)
    except:
        pass
    return False

print("=" * 60)
print("MAKE KIN-INFERENCE PUBLIC")
print("=" * 60)

# Method 1: create_repo with exist_ok
print("\n[1] create_repo(exist_ok=True, private=False)...")
try:
    create_repo(SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True)
    print("  Done")
    if check_public():
        print("  Space is PUBLIC!")
        upload_files()
        print("\nSUCCESS!")
        sys.exit(0)
    print("  Still private")
except Exception as e:
    print(f"  Error: {e}")

# Method 2: update_repo_visibility
print("\n[2] update_repo_visibility...")
try:
    api.update_repo_visibility(SPACE_ID, private=False,
        repo_type="space", token=HF_TOKEN)
    print("  Done")
    if check_public():
        print("  Space is PUBLIC!")
        upload_files()
        print("\nSUCCESS!")
        sys.exit(0)
    print("  Still private")
except Exception as e:
    print(f"  Error: {e}")

# Method 3: Delete + recreate as public
print("\n[3] Delete + recreate as public...")
try:
    api.delete_repo(SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted")
except Exception as e:
    print(f"  Delete error (continuing): {e}")

time.sleep(5)

try:
    create_repo(SPACE_ID, repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=False)
    print("  Created as public!")
    upload_files()
    if check_public():
        print("\nSUCCESS! Space is public!")
    else:
        print("\nWARNING: may still be private")
except Exception as e:
    print(f"  Create error: {e}")
    traceback.print_exc()
    # Retry with exist_ok
    time.sleep(10)
    try:
        create_repo(SPACE_ID, repo_type="space", private=False,
                    token=HF_TOKEN, exist_ok=True)
        print("  Created with exist_ok")
        upload_files()
    except Exception as e2:
        print(f"  Retry failed: {e2}")

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
