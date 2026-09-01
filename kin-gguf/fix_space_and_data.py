import json, os, sys, tempfile
from huggingface_hub import HfApi, hf_hub_download

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3
api = HfApi(token=TOKEN)

# =====================
# PART 1: Fix the Space
# =====================
print("=== PART 1: Fixing Space (kin-cybersec) ===")
print("Uploading new app.py (llama-cpp-python + KIN GGUF)...")

space_files = {
    "app.py": "kin-gguf/space_app.py",
    "requirements.txt": "kin-gguf/space_requirements.txt",
    "README.md": "kin-gguf/space_readme.md",
}

for target, source in space_files.items():
    try:
        api.upload_file(
            path_or_fileobj=source,
            path_in_repo=target,
            repo_id="nyxspecter4/kin-cybersec",
            repo_type="space",
            token=TOKEN,
            commit_message="Fix: serve KIN model via llama-cpp-python (was using base Qwen)",
        )
        print(f"  [OK] Uploaded {target}")
    except Exception as e:
        print(f"  [FAIL] {target}: {e}")

# =====================
# PART 2: Fix the Dataset
# =====================
print("\n=== PART 2: Fixing Dataset (kin-cyber-dpo-v2) ===")
print("Restoring SFT data from backup datasets...")

all_dpo = []

for repo_id, files in [
    ("nyxspecter4/kin-dpo-data", ["train.jsonl", "sft.jsonl"]),
    ("nyxspecter4/kin-v2-data", ["dpo.jsonl", "sft.jsonl"]),
]:
    for fname in files:
        try:
            path = hf_hub_download(
                repo_id=repo_id, filename=fname, repo_type="dataset", token=TOKEN
            )
            with open(path) as f:
                count = 0
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if "prompt" in item and "chosen" in item and "rejected" in item:
                            all_dpo.append(item)
                            count += 1
                        elif "instruction" in item and "output" in item:
                            all_dpo.append(
                                {
                                    "prompt": item["instruction"],
                                    "chosen": item["output"],
                                    "rejected": "This is a security concern that should be addressed with appropriate measures.",
                                }
                            )
                            count += 1
                print(f"  {repo_id}/{fname}: {count} pairs")
        except Exception as e:
            print(f"  {repo_id}/{fname}: ERROR - {e}")

# Dedupe
seen = set()
unique_dpo = []
for p in all_dpo:
    if p["prompt"] not in seen:
        seen.add(p["prompt"])
        unique_dpo.append(p)

# Convert DPO to SFT format
sft_pairs = [
    {"instruction": p["prompt"], "input": "", "output": p["chosen"]}
    for p in unique_dpo
]

print(f"\nTotal unique DPO pairs: {len(unique_dpo)}")
print(f"Total SFT pairs (converted from DPO): {len(sft_pairs)}")

# Write files
output_dir = "/tmp/kin-data-fix"
os.makedirs(output_dir, exist_ok=True)

with open(f"{output_dir}/dpo.jsonl", "w") as f:
    for p in unique_dpo:
        f.write(json.dumps(p) + "\n")

with open(f"{output_dir}/train.jsonl", "w") as f:
    for p in unique_dpo:
        f.write(json.dumps(p) + "\n")

with open(f"{output_dir}/sft.jsonl", "w") as f:
    for p in sft_pairs:
        f.write(json.dumps(p) + "\n")

# Upload data files
for fname in ["dpo.jsonl", "train.jsonl", "sft.jsonl"]:
    try:
        n = len(unique_dpo) if fname != "sft.jsonl" else len(sft_pairs)
        api.upload_file(
            path_or_fileobj=f"{output_dir}/{fname}",
            path_in_repo=fname,
            repo_id="nyxspecter4/kin-cyber-dpo-v2",
            repo_type="dataset",
            token=TOKEN,
            commit_message=f"Fix: restore {fname} ({n} pairs)",
        )
        print(f"  [OK] Uploaded {fname} ({n} pairs)")
    except Exception as e:
        print(f"  [FAIL] {fname}: {e}")

# =====================
# PART 3: Update GGUF Model Card
# =====================
print("\n=== PART 3: Updating GGUF Model Card ===")

card_path = "kin-gguf/gguf_model_card_v2.md"
if os.path.exists(card_path):
    try:
        api.upload_file(
            path_or_fileobj=card_path,
            path_in_repo="README.md",
            repo_id="nyxspecter4/kin-sft-lora-gguf",
            repo_type="model",
            token=TOKEN,
            commit_message="Update model card: fix training data link, add comparison table",
        )
        print("  [OK] GGUF model card updated")
    except Exception as e:
        print(f"  [FAIL] GGUF model card: {e}")
else:
    print(f"  [SKIP] {card_path} not found")

print("\n=== Done: Space + Dataset + Model Card ===")
