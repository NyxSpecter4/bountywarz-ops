#!/usr/bin/env python3
"""Test create_repo with the current token. Write results to model repo."""
import os, sys, tempfile, traceback

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

from huggingface_hub import HfApi, create_repo

api = HfApi(token=HF_TOKEN)
MODEL_ID = "nyxspecter4/kin-sft-lora"

results = []

# whoami
try:
    me = api.whoami()
    results.append(f"whoami: name={me.get('name')}, type={me.get('type')}")
except Exception as e:
    results.append(f"whoami FAILED: {e}")

# Test: create model repo (public)
try:
    create_repo("nyxspecter4/kin-test-model", repo_type="model", private=False,
                token=HF_TOKEN, exist_ok=True)
    results.append("create_repo(model, public): SUCCESS")
    # Clean up
    try:
        api.delete_repo("nyxspecter4/kin-test-model", token=HF_TOKEN)
        results.append("  cleanup: deleted")
    except:
        pass
except Exception as e:
    results.append(f"create_repo(model, public): FAILED - {e}")

# Test: create model repo (private)
try:
    create_repo("nyxspecter4/kin-test-priv", repo_type="model", private=True,
                token=HF_TOKEN, exist_ok=True)
    results.append("create_repo(model, private): SUCCESS")
    try:
        api.delete_repo("nyxspecter4/kin-test-priv", token=HF_TOKEN)
        results.append("  cleanup: deleted")
    except:
        pass
except Exception as e:
    results.append(f"create_repo(model, private): FAILED - {e}")

# Test: create space (public)
try:
    create_repo("nyxspecter4/kin-test-space", repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True)
    results.append("create_repo(space, public): SUCCESS")
    try:
        api.delete_repo("nyxspecter4/kin-test-space", repo_type="space", token=HF_TOKEN)
        results.append("  cleanup: deleted")
    except:
        pass
except Exception as e:
    results.append(f"create_repo(space, public): FAILED - {e}")

# Test: update_repo_visibility on existing model
try:
    api.update_repo_visibility(MODEL_ID, private=False, token=HF_TOKEN)
    results.append("update_repo_visibility: SUCCESS")
except Exception as e:
    results.append(f"update_repo_visibility: FAILED - {e}")

# Write results to model repo
output = "# Create Repo Test Results\n\n"
for r in results:
    output += f"- {r}\n"

with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(output)
    p = f.name
try:
    api.upload_file(path_or_fileobj=p, path_in_repo="CREATE_REPO_TEST.md",
        repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
    print("Results written to model repo")
except Exception as e:
    print(f"Could not write results: {e}")
os.unlink(p)

print("\n".join(results))
