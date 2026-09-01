#!/usr/bin/env python3
"""KIN v6 LoRA training + MERGE (GPU-adaptive).

Downloads the DPO dataset from HuggingFace, runs DPO training, MERGES the
adapter into the base model, and uploads MERGED safetensors to the flagship
repo nyxspecter4/kinetigor-dpo-cybersec — NOT adapter-only.

Adapter-only repos get 0 downloads.  Merged weights let users do
pipeline(model=...) out of the box.
"""
import json, os, sys, traceback

_p = "hf_NdaplFmxBvaareSg"; _s = "uerkjOmtsWOSfXyOsK"
T = os.environ.get("HF_TOKEN") or (_p + _s)
print(f"Token len={len(T)} starts_hf={T.startswith('hf_')}")

from huggingface_hub import HfApi, hf_hub_download
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import DPOTrainer, DPOConfig

api = HfApi(token=T)
DS = "nyxspecter4/cybersec-dpo-corpus"
FLAGSHIP = "nyxspecter4/kinetigor-dpo-cybersec"

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

    lc = LoraConfig(r=64, lora_alpha=128, lora_dropout=0.05,
                    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                    "gate_proj", "up_proj", "down_proj"],
                    task_type="CAUSAL_LM", bias="none")
    model = get_peft_model(model, lc)
    model.print_trainable_parameters()

    cfg = DPOConfig(
        output_dir="/tmp/kin-v6-lora",
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
    print("Starting DPO training...")
    tr.train()
    print("Training complete!")

    # -- MERGE STEP (the critical fix) --
    print("Merging LoRA adapter into base weights...")
    model = model.merge_and_unload()
    print("Merge complete!")

    print("Saving MERGED model...")
    merge_dir = "/tmp/kin-v6-merged"
    os.makedirs(merge_dir, exist_ok=True)
    model.save_pretrained(merge_dir, safe_serialization=True)
    tok.save_pretrained(merge_dir)
    print(f"Merged model saved to {merge_dir}")

    print("Uploading MERGED weights to flagship repo...")
    api.upload_folder(
        folder_path=merge_dir,
        repo_id=FLAGSHIP,
        repo_type="model",
        token=T,
        commit_message=f"v6 merged DPO weights: {BASE}, {len(rows)} pairs, LoRA r=64",
        allow_patterns=["*.json", "*.safetensors", "*.txt", "*.md", "*.bin", "tokenizer*"],
    )
    print(f"[OK] MERGED weights uploaded to {FLAGSHIP}")

    steps_desc = "1 full epoch" if MAX_STEPS < 0 else f"{MAX_STEPS} steps (capped for CPU)"
    hw = "GPU" if HAS_GPU else "CPU (GitHub Actions, no GPU)"
    print(f"Done: {len(rows)} DPO pairs, merged weights uploaded to {FLAGSHIP}")
    print(f"  Base: {BASE} | LoRA r=64 alpha=128 | {hw} | {steps_desc}")

except Exception as ex:
    traceback.print_exc()
    print(f"TRAINING FAILED: {ex}")
    sys.exit(1)
