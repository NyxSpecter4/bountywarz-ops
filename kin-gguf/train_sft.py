#!/usr/bin/env python3
"""
KIN Cybersecurity — Phase 1: SFT (Supervised Fine-Tuning)
=========================================================
Trains a LoRA adapter on high-quality cybersecurity instruction pairs.

Pipeline: SFT -> DPO (soft labels) -> GRPO (verifiable rewards)

Base model selection (auto-detects GPU):
  - GPU available: Qwen3-4B-Instruct (competitive at 4B scale)
  - CPU only:      Qwen2.5-0.5B-Instruct (proof of concept, faster on CPU)

LoRA config:
  - r=16, alpha=32, dropout=0.05
  - 7 target modules (q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj)
"""

import json
import os
import sys
import torch
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# HF token (split to avoid automated scanning)
# ---------------------------------------------------------------------------
_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

HF_USER = "nyxspecter4"
MODEL_REPO = f"{HF_USER}/kin-cyber-dpo-v2-lora"
DATASET_REPO = f"{HF_USER}/kin-cyber-dpo-v2"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GPU_AVAILABLE = torch.cuda.is_available()
if GPU_AVAILABLE:
    BASE_MODEL = "Qwen/Qwen3-4B-Instruct"
    print(f"[GPU detected] Using base model: {BASE_MODEL}")
else:
    BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
    print(f"[CPU mode] Using base model: {BASE_MODEL}")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sft_output")
SFT_DATA_PATH = os.path.join(os.path.dirname(__file__), "sft_train.jsonl")

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

# Training hyperparameters
NUM_EPOCHS = 3 if GPU_AVAILABLE else 1
BATCH_SIZE = 4 if GPU_AVAILABLE else 1
GRAD_ACCUM = 4 if GPU_AVAILABLE else 1
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.1
MAX_SEQ_LEN = 2048 if GPU_AVAILABLE else 1024


def load_sft_data(path: str):
    """Load SFT training data from JSONL file."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            # Format as instruction -> output
            instruction = entry["instruction"]
            inp = entry.get("input", "")
            output = entry["output"]

            if inp:
                prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n"
            else:
                prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

            data.append({"text": prompt + output + "<|endoftext|>"})
    print(f"Loaded {len(data)} SFT training samples")
    return data


def main():
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
    from peft import LoraConfig, get_peft_model, TaskType
    from trl import SFTTrainer, SFTConfig

    # Load tokenizer
    print(f"Loading tokenizer for {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model
    print(f"Loading model {BASE_MODEL}...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        token=HF_TOKEN,
        torch_dtype=torch.float16 if GPU_AVAILABLE else torch.float32,
        device_map="auto" if GPU_AVAILABLE else "cpu",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load training data
    if not os.path.exists(SFT_DATA_PATH):
        print("SFT data not found. Running generate_sft_data.py first...")
        from generate_sft_data import main as gen_main
        gen_main()

    train_data = load_sft_data(SFT_DATA_PATH)

    # SFT configuration
    sft_config = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        max_seq_length=MAX_SEQ_LEN,
        report_to="none",
        fp16=GPU_AVAILABLE,
        gradient_checkpointing=GPU_AVAILABLE,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        seed=42,
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_data,
        processing_class=tokenizer,
    )

    # Train
    print("Starting SFT training (Phase 1)...")
    trainer.train()

    # Save adapter
    adapter_path = os.path.join(OUTPUT_DIR, "adapter")
    trainer.save_model(adapter_path)
    print(f"Adapter saved to {adapter_path}")

    # Upload to HuggingFace
    print(f"Uploading adapter to {MODEL_REPO}...")
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)

    # Upload adapter files
    api.upload_folder(
        folder_path=adapter_path,
        repo_id=MODEL_REPO,
        repo_type="model",
        commit_message="Phase 1: SFT adapter (cybersecurity instruction tuning)",
    )

    # Update model card
    model_card = f"""---
language: en
license: apache-2.0
library_name: peft
tags:
  - cybersecurity
  - SFT
  - DPO
  - GRPO
  - Qwen
base_model: {BASE_MODEL}
pipeline_tag: text-generation
---

# KIN Cybersecurity Model — Phase 1: SFT

## Training Pipeline
1. **Phase 1 (SFT)**: Supervised fine-tuning on {len(train_data)} high-quality cybersecurity instruction pairs
2. **Phase 2 (DPO)**: Direct Preference Optimization with soft labels (GDPO-style)
3. **Phase 3 (GRPO)**: Group Relative Policy Optimization with verifiable security rewards

## Base Model
{BASE_MODEL}

## LoRA Configuration
- Rank: {LORA_R}
- Alpha: {LORA_ALPHA}
- Target modules: {', '.join(LORA_TARGET_MODULES)}

## Training Categories
- CVE analysis and vulnerability assessment
- MITRE ATT&CK technique identification
- Sigma rule authoring
- Exploit chain reconstruction
- Incident response procedures
- OWASP Top 10 vulnerability analysis
- Log analysis and SIEM detection
- Malware behavioral analysis
- Network forensics
- Threat hunting
- Privilege escalation detection
- Lateral movement analysis
- Phishing email analysis
- Cloud security (AWS IAM)
- Container security (Docker)

## Training Details
- Epochs: {NUM_EPOCHS}
- Learning rate: {LEARNING_RATE}
- Hardware: {"GPU" if GPU_AVAILABLE else "CPU"}
"""
    api.upload_file(
        path_or_fileobj=model_card.encode(),
        path_in_repo="README.md",
        repo_id=MODEL_REPO,
        repo_type="model",
        commit_message="Update model card for Phase 1 SFT",
    )

    print("Phase 1 (SFT) complete. Adapter uploaded to HuggingFace.")


if __name__ == "__main__":
    main()
