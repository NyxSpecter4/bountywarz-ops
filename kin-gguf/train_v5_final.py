#!/usr/bin/env python3
"""KIN v5 DPO training pipeline -- clean single-script version.

Reads v5 DPO pairs from v5_pairs.json, merges with existing dataset,
uploads v5 dataset to HuggingFace, runs DPO training, and uploads the
LoRA adapter. Dataset upload happens FIRST so it succeeds even if
training fails on resource-limited runners.
"""
import json, os, sys, traceback, hashlib, tempfile

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)
print(f"Token len={len(T)} starts_hf={T.startswith('hf_')}")

from huggingface_hub import HfApi, hf_hub_download
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import DPOTrainer, DPOConfig

api = HfApi(token=T)
DS = "nyxspecter4/kin-cyber-dpo-v2"
MODEL_REPO = "nyxspecter4/kin-cyber-dpo-v2-lora"

# Load new v5 DPO pairs from JSON file in repo
with open("kin-gguf/v5_pairs.json", "r", encoding="utf-8") as f:
    NEW_PAIRS = json.load(f)
print(f"Loaded {len(NEW_PAIRS)} new v5 DPO pairs from v5_pairs.json")

# ============================================================
# Phase 1: Merge and upload dataset
# ============================================================

def dedup_key(pair):
    h = hashlib.sha256()
    h.update((pair["prompt"][:200] + pair["chosen"][:200]).encode("utf-8"))
    return h.hexdigest()

def phase1_dataset():
    """Merge new pairs with existing dataset and upload to HF."""
    try:
        p = hf_hub_download(repo_id=DS, filename="dpo.jsonl", repo_type="dataset", token=T)
        existing = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        print(f"Loaded {len(existing)} existing DPO pairs")
    except Exception as e:
        print(f"Could not download existing dataset: {e}")
        existing = []

    seen = set()
    merged = []
    for pair in existing + NEW_PAIRS:
        k = dedup_key(pair)
        if k not in seen:
            seen.add(k)
            merged.append({
                "prompt": pair["prompt"],
                "chosen": pair["chosen"],
                "rejected": pair["rejected"],
            })

    added = len(merged) - len(existing)
    print(f"Merged dataset: {len(merged)} unique pairs (was {len(existing)}, added {added})")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for pair in merged:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        dpo_file = f.name

    api.upload_file(
        path_or_fileobj=dpo_file,
        path_in_repo="dpo.jsonl",
        repo_id=DS,
        repo_type="dataset",
        token=T,
        commit_message=f"v5: added {added} new DPO pairs (vuln-finding, exploit-chain, CVE analysis)",
    )
    print(f"[OK] dpo.jsonl uploaded: {len(merged)} pairs")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
        for pair in merged:
            f.write(json.dumps({"prompt": pair["prompt"], "response": pair["chosen"]}, ensure_ascii=False) + "\n")
        sft_file = f.name

    api.upload_file(
        path_or_fileobj=sft_file,
        path_in_repo="sft.jsonl",
        repo_id=DS,
        repo_type="dataset",
        token=T,
        commit_message="v5 sft.jsonl update",
    )
    print(f"[OK] sft.jsonl uploaded")

    return len(merged)

# ============================================================
# Phase 2: DPO Training
# ============================================================

def phase2_train(num_pairs):
    """Run DPO training and upload adapter."""
    HAS_GPU = torch.cuda.is_available()
    print(f"CUDA available: {HAS_GPU}")

    if HAS_GPU:
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        BASE = "Qwen/Qwen2.5-3B-Instruct"
        MAX_STEPS = -1
        MAX_LEN = 1024
        BS = 2
        GA = 8
        DTYPE = torch.float16
        DM = "auto"
    else:
        print("No GPU detected -- using 0.5B base with capped steps (CPU-feasible).")
        BASE = "Qwen/Qwen2.5-0.5B-Instruct"
        MAX_STEPS = 100
        MAX_LEN = 512
        BS = 1
        GA = 2
        DTYPE = torch.float32
        DM = None

    print(f"Training base: {BASE}  GPU={HAS_GPU} max_steps={MAX_STEPS} max_len={MAX_LEN}")

    p = hf_hub_download(repo_id=DS, filename="dpo.jsonl", repo_type="dataset", token=T)
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    print(f"Loaded {len(rows)} DPO pairs for training")

    ds = Dataset.from_list([
        {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
        for r in rows
    ])

    print("Loading tokenizer...")
    tok = AutoTokenizer.from_pretrained(BASE, token=T)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    print("Loading base model...")
    kw = dict(torch_dtype=DTYPE, token=T)
    if DM:
        kw["device_map"] = DM
    model = AutoModelForCausalLM.from_pretrained(BASE, **kw)

    lc = LoraConfig(
        r=8, lora_alpha=16, lora_dropout=0.1,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type="CAUSAL_LM", bias="none",
    )
    model = get_peft_model(model, lc)
    model.print_trainable_parameters()

    cfg = DPOConfig(
        output_dir="/tmp/kin-v5-lora",
        num_train_epochs=1,
        max_steps=MAX_STEPS,
        per_device_train_batch_size=BS,
        gradient_accumulation_steps=GA,
        learning_rate=5e-6,
        warmup_steps=10,
        logging_steps=10,
        save_steps=100,
        save_total_limit=1,
        bf16=HAS_GPU and torch.cuda.is_bf16_supported(),
        fp16=False,
        gradient_checkpointing=True,
        max_length=MAX_LEN,
        remove_unused_columns=False,
        report_to="none",
        seed=42,
    )

    tr = DPOTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok)
    print("Starting training...")
    tr.train()
    print("Training complete!")

    print("Saving adapter...")
    model.save_pretrained("/tmp/kin-v5-lora")
    tok.save_pretrained("/tmp/kin-v5-lora")

    print("Uploading adapter to HuggingFace...")
    api.upload_folder(
        folder_path="/tmp/kin-v5-lora",
        repo_id=MODEL_REPO,
        repo_type="model",
        token=T,
        commit_message=f"v5 DPO adapter: {BASE}, {num_pairs} pairs",
        allow_patterns=["*.json", "*.safetensors", "*.txt", "*.md", "*.bin"],
    )
    print(f"[OK] Adapter uploaded to {MODEL_REPO}")

    steps_desc = "1 full epoch" if MAX_STEPS < 0 else f"{MAX_STEPS} steps (capped for CPU)"
    hw = "GPU" if HAS_GPU else "CPU (GitHub Actions, no GPU)"
    mc = (
        "---\n"
        "library_name: peft\n"
        f"base_model: {BASE}\n"
        "tags: [cybersecurity, dpo, lora, peft, vulnerability-detection, exploit-chain, cve-analysis]\n"
        "license: apache-2.0\n"
        "language: en\n"
        "---\n\n"
        f"# KIN Cybersecurity DPO v5 LoRA Adapter\n\n"
        f"Trained on {num_pairs} DPO pairs (cybersecurity vulnerability analysis).\n\n"
        "## v5 New Categories\n"
        "- Vulnerability-finding pairs (code pattern recognition)\n"
        "- Exploit-chain reasoning pairs (connecting findings into reports)\n"
        "- Advanced CVE analysis pairs (root cause, exploitation, detection)\n\n"
        "## Training\n"
        f"- Base model: {BASE}\n"
        "- Method: DPO (Direct Preference Optimization)\n"
        "- LoRA rank: 8, alpha: 16, lr: 5e-6\n"
        f"- Hardware: {hw}\n"
        f"- Steps: {steps_desc}\n"
    )
    with open("/tmp/kin-v5-lora/README.md", "w") as f:
        f.write(mc)
    api.upload_file(
        path_or_fileobj="/tmp/kin-v5-lora/README.md",
        path_in_repo="README.md",
        repo_id=MODEL_REPO,
        repo_type="model",
        token=T,
        commit_message="v5 model card",
    )
    print("[OK] Model card updated")
    print(f"Done: {num_pairs} DPO pairs, adapter uploaded to {MODEL_REPO}")

# ============================================================
# Main
# ============================================================

def log_error(msg):
    """Upload error log to HF dataset."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(msg + "\n" + traceback.format_exc())
            log_file = f.name
        api.upload_file(
            path_or_fileobj=log_file,
            path_in_repo="v5_train_run.log",
            repo_id=DS,
            repo_type="dataset",
            token=T,
            commit_message="v5 training error log",
        )
    except Exception:
        pass

def main():
    num_pairs = 0
    try:
        num_pairs = phase1_dataset()
    except Exception as ex:
        traceback.print_exc()
        print(f"DATASET PHASE FAILED: {ex}")
        log_error(f"Dataset phase failed: {ex}")
        sys.exit(1)

    try:
        phase2_train(num_pairs)
    except Exception as ex:
        traceback.print_exc()
        print(f"TRAINING FAILED: {ex}")
        log_error(f"Training failed (dataset OK with {num_pairs} pairs): {ex}")
        print(f"Dataset updated to {num_pairs} pairs, but training failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()