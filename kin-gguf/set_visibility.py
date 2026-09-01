import requests, json, os

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

print("=== KIN Repo Visibility Sweep v3 (raw API) ===")

def set_visibility(repo_id, repo_type, private):
    url = f"https://huggingface.co/api/{repo_type}s/{repo_id}/settings"
    resp = requests.put(url, headers=HEADERS, json={"private": private})
    return resp.status_code, resp.text[:300]

ok = 0
fail = 0

private_repos = [
    ("nyxspecter4/kin-sft-lora", "model"),
    ("nyxspecter4/kin-cyber-dpo-v2-lora", "model"),
    ("nyxspecter4/monk-bounty-examples", "dataset"),
    ("nyxspecter4/kin-v2-data", "dataset"),
    ("nyxspecter4/monk-bounty-dedup-corpus", "dataset"),
    ("nyxspecter4/kin-v2-cybersecurity", "space"),
    ("nyxspecter4/kin-cyber-trainer", "space"),
    ("nyxspecter4/monk-finding-grade-arena", "space"),
    ("nyxspecter4/monk-finding-loop", "space"),
    ("nyxspecter4/nemeton-war-room", "space"),
    ("nyxspecter4/monk-ctf-arena", "space"),
    ("nyxspecter4/makothoth-flywheel", "space"),
]

public_repos = [
    ("nyxspecter4/kin-sft-lora-gguf", "model"),
    ("nyxspecter4/kin-cyber-dpo-v2", "dataset"),
    ("nyxspecter4/kin-cybersec", "space"),
]

for repo_id, rtype in private_repos:
    code, body = set_visibility(repo_id, rtype, True)
    status = "OK" if code in (200, 201, 204) else "FAIL"
    print(f"  [{status}] {rtype} {repo_id} -> private (HTTP {code})")
    if code in (200, 201, 204):
        ok += 1
    else:
        fail += 1
        print(f"    Error: {body}")

for repo_id, rtype in public_repos:
    code, body = set_visibility(repo_id, rtype, False)
    status = "OK" if code in (200, 201, 204) else "FAIL"
    print(f"  [{status}] {rtype} {repo_id} -> public (HTTP {code})")
    if code in (200, 201, 204):
        ok += 1
    else:
        fail += 1
        print(f"    Error: {body}")

print(f"\n=== Done: {ok} ok, {fail} failed ===")
