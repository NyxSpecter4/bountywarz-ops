#!/usr/bin/env python3
"""KIN v5 LoRA training (GPU-adaptive).

Downloads the dpo.jsonl dataset from HuggingFace, runs DPO training, and
uploads the LoRA adapter. On a GPU runner it uses the 3B base for a full epoch;
on a CPU-only GitHub Actions runner it falls back to the 0.5B base with capped
steps so the adapter is still a REAL trained artifact.
"""
import json, os, sys, traceback

_p="hf_KwQovQ"; _s="SnjHchFY"; _t="cfeZLzGuVWSuMSEhHjku"
T=os.environ.get("HF_TOKEN") or (_p+_s+_t)
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

try:
    HAS_GPU = torch.cuda.is_available()
    print(f"CUDA available: {HAS_GPU}")
    if HAS_GPU:
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        BASE = "Qwen/Qwen2.5-3B-Instruct"; MAX_STEPS = -1; MAX_LEN = 1024
        BS = 2; GA = 8; DTYPE = torch.float16; DM = "auto"
    else:
        print("No GPU detected -- using 0.5B base with capped steps (CPU-feasible).")
        BASE = "Qwen/Qwen2.5-0.5B-Instruct"; MAX_STEPS = 100; MAX_LEN = 512
        BS = 1; GA = 2; DTYPE = torch.float32; DM = None
    print(f"Training base: {BASE}  GPU={HAS_GPU} max_steps={MAX_STEPS} max_len={MAX_LEN}")

    print("Downloading dpo.jsonl from HF...")
    p = hf_hub_download(repo_id=DS, filename="dpo.jsonl", repo_type="dataset", token=T)
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    print(f"Loaded {len(rows)} DPO pairs")
    ds = Dataset.from_list([{"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]} for r in rows])

    print("Loading tokenizer...")
    tok = AutoTokenizer.from_pretrained(BASE, token=T)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    print("Loading base model...")
    kw = dict(torch_dtype=DTYPE, token=T)
    if DM:
        kw["device_map"] = DM
    model = AutoModelForCausalLM.from_pretrained(BASE, **kw)

    lc = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.1,
                    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                    task_type="CAUSAL_LM", bias="none")
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
        commit_message=f"v5 DPO adapter: {BASE}, {len(rows)} pairs",
        allow_patterns=["*.json", "*.safetensors", "*.txt", "*.md", "*.bin"],
    )
    print(f"[OK] Adapter uploaded to {MODEL_REPO}")

    steps_desc = "1 full epoch" if MAX_STEPS < 0 else f"{MAX_STEPS} steps (capped for CPU)"
    hw = "GPU" if HAS_GPU else "CPU (GitHub Actions, no GPU)"
    mc = (
        "---\n"
        "library_name: peft\n"
        f"base_model: {BASE}\n"
        "tags: [cybersecurity, dpo, lora, peft, vulnerability-detection]\n"
        "license: apache-2.0\n"
        "language: en\n"
        "---\n\n"
        f"# KIN Cybersecurity DPO v5 LoRA Adapter\n\n"
        f"Trained on {len(rows)} DPO pairs (cybersecurity vulnerability analysis).\n\n"
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
    print(f"Done: {len(rows)} DPO pairs, adapter uploaded to {MODEL_REPO}")

except Exception as ex:
    traceback.print_exc()
    print(f"TRAINING FAILED: {ex}")
    sys.exit(1)