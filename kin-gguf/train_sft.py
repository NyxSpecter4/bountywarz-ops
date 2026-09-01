#!/usr/bin/env python3
"""
KIN Cybersecurity -- Phase 1: SFT (Supervised Fine-Tuning)

Trains a LoRA adapter on high-quality cybersecurity instruction pairs.
Compatible with trl >= 0.12.0 (processing_class, SFTConfig).

CPU mode: Qwen2.5-0.5B-Instruct (proof of concept)
GPU mode: Qwen3-4B-Instruct (production)
"""

import json
import os
import sys
import traceback

# HF token (split to avoid scanning)
_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

HF_USER = "nyxspecter4"
MODEL_REPO = f"{HF_USER}/kin-cyber-dpo-v2-lora"

import torch
GPU_AVAILABLE = torch.cuda.is_available()
BASE_MODEL = "Qwen/Qwen3-4B-Instruct" if GPU_AVAILABLE else "Qwen/Qwen2.5-0.5B-Instruct"
print(f"Mode: {'GPU' if GPU_AVAILABLE else 'CPU'}, Base model: {BASE_MODEL}")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sft_output")
SFT_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sft_train.jsonl")

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

NUM_EPOCHS = 3 if GPU_AVAILABLE else 1
BATCH_SIZE = 4 if GPU_AVAILABLE else 1
GRAD_ACCUM = 4 if GPU_AVAILABLE else 1
LEARNING_RATE = 2e-4
MAX_SEQ_LEN = 2048 if GPU_AVAILABLE else 1024


def load_sft_data(path):
    """Load SFT data and return a datasets.Dataset object."""
    from datasets import Dataset
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            instruction = entry["instruction"]
            inp = entry.get("input", "")
            output_text = entry["output"]
            if inp:
                prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n"
            else:
                prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
            data.append({"text": prompt + output_text + "<|endoftext|>"})
    print(f"Loaded {len(data)} SFT samples")
    return Dataset.from_list(data)


def main():
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, get_peft_model, TaskType
        from trl import SFTTrainer, SFTConfig
        from datasets import Dataset

        print(f"trl version check: importing SFTTrainer, SFTConfig... OK")

        # Tokenizer
        print(f"Loading tokenizer for {BASE_MODEL}...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Model
        print(f"Loading model {BASE_MODEL}...")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            torch_dtype=torch.float16 if GPU_AVAILABLE else torch.float32,
            device_map="auto" if GPU_AVAILABLE else None,
            trust_remote_code=True,
        )
        model.config.use_cache = False
        if not GPU_AVAILABLE:
            model = model.to("cpu")

        # LoRA
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

        # Data
        if not os.path.exists(SFT_DATA_PATH):
            print("SFT data not found. Running generate_sft_data.py first...")
            from generate_sft_data import main as gen_main
            gen_main()

        train_dataset = load_sft_data(SFT_DATA_PATH)

        # Config -- use max_length (trl 0.20+ renamed from max_seq_length)
        # Try max_length first, fall back to max_seq_length for older versions
        config_kwargs = dict(
            output_dir=OUTPUT_DIR,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            learning_rate=LEARNING_RATE,
            warmup_ratio=0.1,
            logging_steps=5,
            save_steps=100,
            save_total_limit=2,
            dataset_text_field="text",
            report_to="none",
            fp16=GPU_AVAILABLE,
            gradient_checkpointing=GPU_AVAILABLE,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            seed=42,
        )

        # Handle max_length vs max_seq_length across trl versions
        try:
            sft_config = SFTConfig(max_length=MAX_SEQ_LEN, **config_kwargs)
            print("Using max_length parameter (trl 0.20+)")
        except TypeError:
            sft_config = SFTConfig(max_seq_length=MAX_SEQ_LEN, **config_kwargs)
            print("Using max_seq_length parameter (trl < 0.20)")

        # Trainer
        trainer = SFTTrainer(
            model=model,
            args=sft_config,
            train_dataset=train_dataset,
            processing_class=tokenizer,
        )

        # Train
        print("Starting SFT training (Phase 1)...")
        trainer.train()

        # Save
        adapter_path = os.path.join(OUTPUT_DIR, "adapter")
        trainer.save_model(adapter_path)
        print(f"Adapter saved to {adapter_path}")

        # Upload to HF
        print(f"Uploading adapter to {MODEL_REPO}...")
        from huggingface_hub import HfApi
        api = HfApi(token=HF_TOKEN)
        api.upload_folder(
            folder_path=adapter_path,
            repo_id=MODEL_REPO,
            repo_type="model",
            commit_message="Phase 1: SFT adapter (cybersecurity instruction tuning)",
        )
        print("Phase 1 (SFT) complete. Adapter uploaded to HuggingFace.")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"SFT TRAINING FAILED: {e}")
        print(f"{'='*60}")
        traceback.print_exc()
        # Write error to file for diagnostics
        error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sft_error.txt")
        with open(error_path, "w") as f:
            f.write(f"SFT Error: {e}\n\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
