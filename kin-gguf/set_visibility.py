import os, sys
from huggingface_hub import HfApi

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3

api = HfApi(token=TOKEN)

print("=== KIN Repo Visibility Sweep ===")
print("Goal: 1 public model, 1 public dataset, 1 public space")

PUBLIC_MODEL = "nyxspecter4/kin-sft-lora-gguf"
PUBLIC_DATASET = "nyxspecter4/kin-cyber-dpo-v2"
PUBLIC_SPACE = "nyxspecter4/kin-cybersec"

PRIVATE_MODELS = [
    "nyxspecter4/kin-sft-lora",
    "nyxspecter4/kin-cyber-dpo-v2-lora",
]

PRIVATE_DATASETS = [
    "nyxspecter4/monk-bounty-examples",
    "nyxspecter4/kin-v2-data",
    "nyxspecter4/monk-bounty-dedup-corpus",
]

PRIVATE_SPACES = [
    "nyxspecter4/kin-v2-cybersecurity",
    "nyxspecter4/kin-cyber-trainer",
    "nyxspecter4/monk-finding-grade-arena",
    "nyxspecter4/monk-finding-loop",
    "nyxspecter4/nemeton-war-room",
    "nyxspecter4/monk-ctf-arena",
    "nyxspecter4/makothoth-flywheel",
]

results = {"ok": [], "fail": []}

for repo_id in PRIVATE_MODELS:
    try:
        api.update_repo_visibility(repo_id=repo_id, repo_type="model", private=True)
        print(f"  [OK] model {repo_id} -> private")
        results["ok"].append(f"model:{repo_id}")
    except Exception as e:
        print(f"  [FAIL] model {repo_id}: {e}")
        results["fail"].append(f"model:{repo_id}:{e}")

for repo_id in PRIVATE_DATASETS:
    try:
        api.update_repo_visibility(repo_id=repo_id, repo_type="dataset", private=True)
        print(f"  [OK] dataset {repo_id} -> private")
        results["ok"].append(f"dataset:{repo_id}")
    except Exception as e:
        print(f"  [FAIL] dataset {repo_id}: {e}")
        results["fail"].append(f"dataset:{repo_id}:{e}")

for repo_id in PRIVATE_SPACES:
    try:
        api.update_repo_visibility(repo_id=repo_id, repo_type="space", private=True)
        print(f"  [OK] space {repo_id} -> private")
        results["ok"].append(f"space:{repo_id}")
    except Exception as e:
        print(f"  [FAIL] space {repo_id}: {e}")
        results["fail"].append(f"space:{repo_id}:{e}")

for repo_id, rtype in [(PUBLIC_MODEL, "model"), (PUBLIC_DATASET, "dataset"), (PUBLIC_SPACE, "space")]:
    try:
        api.update_repo_visibility(repo_id=repo_id, repo_type=rtype, private=False)
        print(f"  [OK] {rtype} {repo_id} -> public (confirmed)")
        results["ok"].append(f"{rtype}:{repo_id}:public")
    except Exception as e:
        print(f"  [SKIP] {rtype} {repo_id}: {e}")
        results["fail"].append(f"{rtype}:{repo_id}:{e}")

print(f"\n=== Done: {len(results['ok'])} ok, {len(results['fail'])} failed ===")
if results["fail"]:
    print("Failures:")
    for f in results["fail"]:
        print(f"  {f}")
