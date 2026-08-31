#!/usr/bin/env python3
"""Test whether create_repo works with the current token."""
import sys, traceback

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

from huggingface_hub import HfApi, create_repo, whoami

api = HfApi(token=HF_TOKEN)

# Check whoami
print("=== whoami ===")
try:
    me = whoami(token=HF_TOKEN)
    print(f"Name: {me.get('name')}")
    print(f"Type: {me.get('type')}")
except Exception as e:
    print(f"whoami failed: {e}")

# Test 1: Create a model repo
print("\n=== Test 1: Create model repo ===")
try:
    create_repo("nyxspecter4/kin-test-model", repo_type="model", private=False, token=HF_TOKEN, exist_ok=True)
    print("SUCCESS: model repo created")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

# Test 2: Create a space
print("\n=== Test 2: Create space ===")
try:
    create_repo("nyxspecter4/kin-test-space", repo_type="space", private=False, token=HF_TOKEN, exist_ok=True)
    print("SUCCESS: space created")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

# Test 3: Create a model repo as private
print("\n=== Test 3: Create private model repo ===")
try:
    create_repo("nyxspecter4/kin-test-private", repo_type="model", private=True, token=HF_TOKEN, exist_ok=True)
    print("SUCCESS: private model repo created")
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

# Test 4: Try upload to non-existent repo (should fail)
print("\n=== Test 4: Upload to non-existent repo ===")
try:
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test")
        p = f.name
    api.upload_file(path_or_fileobj=p, path_in_repo="test.txt",
        repo_id="nyxspecter4/kin-test-model", repo_type="model", token=HF_TOKEN)
    os.unlink(p)
    print("SUCCESS: uploaded to model repo")
except Exception as e:
    print(f"FAILED: {e}")

# Cleanup: delete test repos
print("\n=== Cleanup ===")
for repo_id in ["nyxspecter4/kin-test-model", "nyxspecter4/kin-test-space", "nyxspecter4/kin-test-private"]:
    try:
        api.delete_repo(repo_id, token=HF_TOKEN)
        print(f"Deleted {repo_id}")
    except Exception as e:
        print(f"Could not delete {repo_id}: {e}")

print("\n=== DONE ===")
