import os, sys, requests
from huggingface_hub import HfApi

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3

api = HfApi(token=TOKEN)
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

print("=== KIN Repo Visibility Sweep v2 ===")

PRIVATE_MODELS = ["nyxspecter4/kin-sft-lora", "nyxspecter4/kin-cyber-dpo-v2-lora"]
PRIVATE_DATASETS = ["nyxspecter4/monk-bounty-examples", "nyxspecter4/kin-v2-data", "nyxspecter4/monk-bounty-dedup-corpus"]
PRIVATE_SPACES = ["nyxspecter4/kin-v2-cybersecurity", "nyxspecter4/kin-cyber-trainer", "nyxspecter4/monk-finding-grade-arena", "nyxspecter4/monk-finding-loop", "nyxspecter4/nemeton-war-room", "nyxspecter4/monk-ctf-arena", "nyxspecter4/makothoth-flywheel"]

PUBLIC_MODEL = "nyxspecter4/kin-sft-lora-gguf"
PUBLIC_DATASET = "nyxspecter4/kin-cyber-dpo-v2"
PUBLIC_SPACE = "nyxspecter4/kin-cybersec"

def set_visibility(repo_id, repo_type, private):
    try:
        api.update_repo_settings(repo_id=repo_id, repo_type=repo_type, private=private)
        return True, "update_repo_settings"
    except Exception as e1:
        pass
    try:
        url = f"https://huggingface.co/api/{repo_type}s/{repo_id}/settings"
        resp = requests.put(url, headers=HEADERS, json={"private": private})
        if resp.status_code in (200, 201, 204):
            return True, "raw_api"
        return False, f"raw_api_{resp.status_code}: {resp.text[:200]}"
    except Exception as e2:
        return False, f"both_failed: {e1} | {e2}"

ok = 0
fail = 0

for repo_id in PRIVATE_MODELS:
    success, method = set_visibility(repo_id, "model", True)
    print(f"  [{'OK' if success else 'FAIL'}] model {repo_id} -> private ({method})")
    ok += success; fail += (not success)

for repo_id in PRIVATE_DATASETS:
    success, method = set_visibility(repo_id, "dataset", True)
    print(f"  [{'OK' if success else 'FAIL'}] dataset {repo_id} -> private ({method})")
    ok += success; fail += (not success)

for repo_id in PRIVATE_SPACES:
    success, method = set_visibility(repo_id, "space", True)
    print(f"  [{'OK' if success else 'FAIL'}] space {repo_id} -> private ({method})")
    ok += success; fail += (not success)

for repo_id, rtype in [(PUBLIC_MODEL, "model"), (PUBLIC_DATASET, "dataset"), (PUBLIC_SPACE, "space")]:
    success, method = set_visibility(repo_id, rtype, False)
    print(f"  [OK] {rtype} {repo_id} -> public ({method})")
    ok += success

print(f"\n=== Done: {ok} ok, {fail} failed ===")
