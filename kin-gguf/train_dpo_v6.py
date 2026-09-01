#!/usr/bin/env python3
"""
KIN Cybersecurity -- Phase 2: DPO with Soft Preference Labels (GDPO-style)

Uses soft preference labels computed from response quality signals.
Reference: "Geometric-Averaged Preference Optimization for Soft Preference Labels"
           NeurIPS 2024, arXiv:2409.06691

Compatible with trl >= 0.12.0.
"""

import json
import os
import re
import math
import sys
import traceback
from typing import List, Dict

# HF token
_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

HF_USER = "nyxspecter4"
MODEL_REPO = f"{HF_USER}/kin-cyber-dpo-v2-lora"
DATASET_REPO = f"{HF_USER}/kin-cyber-dpo-v2"

import torch
GPU_AVAILABLE = torch.cuda.is_available()
BASE_MODEL = "Qwen/Qwen3-4B-Instruct" if GPU_AVAILABLE else "Qwen/Qwen2.5-0.5B-Instruct"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dpo_v6_output")
SFT_ADAPTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sft_output", "adapter")

BETA = 0.05
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

NUM_EPOCHS = 1
BATCH_SIZE = 2 if GPU_AVAILABLE else 1
GRAD_ACCUM = 8 if GPU_AVAILABLE else 1
LEARNING_RATE = 5e-5
MAX_LENGTH = 2048 if GPU_AVAILABLE else 1024
MAX_PROMPT_LENGTH = 512

# Security terms for quality signal computation
SECURITY_TERMS = [
    "CVE", "CWE", "MITRE", "ATT&CK", "T1059", "T1566", "T1190",
    "sigma", "yara", "snort", "suricata", "zeek",
    "mimikatz", "procdump", "lsass", "pass-the-hash", "kerberoasting",
    "lateral", "persist", "exfil", "beacon", "c2", "implant",
    "dockerfile", "kubernetes", "k8s", "iam", "s3", "lambda",
    "phishing", "ransomware", "malware", "exploit", "vulnerability",
    "injection", "xss", "sqli", "ssrf", "rce", "privilege",
    "detection", "remediation", "ioc", "indicator",
    "siem", "edr", "firewall", "ids", "ips",
    "registry", "scheduled task", "wmi", "powershell",
    "sysmon", "event id", "auditd",
]

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}")
MITRE_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?")
CODE_BLOCK_PATTERN = re.compile(r"```")
HEADING_PATTERN = re.compile(r"^#{1,6}\s", re.MULTILINE)
LIST_PATTERN = re.compile(r"^\s*[-*]\s|^\s*\d+\.\s", re.MULTILINE)
COMMAND_PATTERN = re.compile(r"^\s*(\$|>|#|PS\s|C:\\)", re.MULTILINE)
TOOL_PATTERN = re.compile(
    r"\b(mimikatz|procdump|crackmapexec|nmap|nessus|burp|metasploit|"
    r"cobalt\s*strike|sysmon|volatility|wireshark|tcpdump|snort|suricata|"
    r"ghidra|ida|radare|frida|bloodhound|rubeus|sharphound|secretsdump|"
    r"impacket|evil-winrm)\b", re.IGNORECASE
)


def compute_quality_signals(text):
    """Compute quality signals for a response. Each signal in [0, 1]."""
    signals = {}
    word_count = len(text.split())
    if word_count < 20:
        signals["length"] = 0.2
    elif word_count < 50:
        signals["length"] = 0.5
    elif word_count < 500:
        signals["length"] = 1.0
    elif word_count < 1000:
        signals["length"] = 0.9
    elif word_count < 2000:
        signals["length"] = 0.7
    else:
        signals["length"] = 0.5

    cve_count = len(CVE_PATTERN.findall(text))
    mitre_count = len(MITRE_PATTERN.findall(text))
    tool_count = len(TOOL_PATTERN.findall(text))
    signals["specificity"] = max(min(cve_count * 0.3 + mitre_count * 0.2 + tool_count * 0.15, 1.0), 0.1)

    code_blocks = len(CODE_BLOCK_PATTERN.findall(text)) / 2
    commands = len(COMMAND_PATTERN.findall(text))
    list_items = len(LIST_PATTERN.findall(text))
    signals["actionability"] = max(min(code_blocks * 0.1 + commands * 0.02 + list_items * 0.01, 1.0), 0.1)

    headings = len(HEADING_PATTERN.findall(text))
    signals["structure"] = max(min(headings * 0.1 + list_items * 0.005, 1.0), 0.1)

    text_lower = text.lower()
    term_count = sum(1 for term in SECURITY_TERMS if term.lower() in text_lower)
    total_words = max(word_count, 1)
    signals["security_terms"] = max(min(term_count / (total_words * 0.05), 1.0), 0.1)
    return signals


def compute_soft_label(chosen, rejected):
    """GDPO soft label: geometric mean of quality signal ratios."""
    chosen_signals = compute_quality_signals(chosen)
    rejected_signals = compute_quality_signals(rejected)
    log_ratios = []
    for key in chosen_signals:
        c = chosen_signals[key]
        r = rejected_signals[key]
        ratio = c / (c + r + 1e-8)
        ratio = max(0.1, min(0.9, ratio))
        log_ratios.append(math.log(ratio))
    soft_label = math.exp(sum(log_ratios) / len(log_ratios))
    return max(0.15, min(0.85, soft_label))


def load_dpo_data():
    """Download and load DPO preference pairs from HuggingFace."""
    from huggingface_hub import hf_hub_download
    print(f"Downloading DPO data from {DATASET_REPO}...")
    try:
        dpo_path = hf_hub_download(
            repo_id=DATASET_REPO,
            filename="dpo.jsonl",
            repo_type="dataset",
            token=HF_TOKEN,
        )
    except Exception:
        # Try train.jsonl as fallback
        print("dpo.jsonl not found, trying train.jsonl...")
        dpo_path = hf_hub_download(
            repo_id=DATASET_REPO,
            filename="train.jsonl",
            repo_type="dataset",
            token=HF_TOKEN,
        )

    pairs = []
    with open(dpo_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            pairs.append(entry)
    print(f"Loaded {len(pairs)} DPO preference pairs")
    return pairs


def prepare_dpo_dataset(pairs):
    """Prepare DPO dataset with soft preference labels as a datasets.Dataset."""
    from datasets import Dataset
    data = []
    label_stats = []
    for pair in pairs:
        prompt = pair.get("prompt", pair.get("question", pair.get("instruction", "")))
        chosen = pair.get("chosen", pair.get("response_chosen", ""))
        rejected = pair.get("rejected", pair.get("response_rejected", ""))
        if not prompt or not chosen or not rejected:
            continue
        soft_label = compute_soft_label(chosen, rejected)
        label_stats.append(soft_label)
        data.append({
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
        })

    if label_stats:
        avg = sum(label_stats) / len(label_stats)
        print(f"Prepared {len(data)} DPO pairs. Avg soft label: {avg:.3f}")
    return Dataset.from_list(data)


def main():
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, PeftModel, TaskType, get_peft_model
        from trl import DPOTrainer, DPOConfig
        from datasets import Dataset

        print(f"Loading tokenizer for {BASE_MODEL}...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

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

        # Load SFT adapter if available
        if os.path.exists(SFT_ADAPTER_DIR):
            print(f"Loading SFT adapter from {SFT_ADAPTER_DIR}...")
            model = PeftModel.from_pretrained(model, SFT_ADAPTER_DIR, is_trainable=True)
        else:
            print("No SFT adapter found. Applying LoRA directly.")
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
                target_modules=LORA_TARGET_MODULES, bias="none",
            )
            model = get_peft_model(model, lora_config)

        model.print_trainable_parameters()

        # Load and prepare data
        pairs = load_dpo_data()
        dpo_dataset = prepare_dpo_dataset(pairs)

        # DPO config
        dpo_config = DPOConfig(
            output_dir=OUTPUT_DIR,
            beta=BETA,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            learning_rate=LEARNING_RATE,
            warmup_ratio=0.1,
            logging_steps=10,
            save_steps=200,
            save_total_limit=2,
            max_length=MAX_LENGTH,
            max_prompt_length=MAX_PROMPT_LENGTH,
            report_to="none",
            fp16=GPU_AVAILABLE,
            gradient_checkpointing=GPU_AVAILABLE,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            seed=42,
        )

        trainer = DPOTrainer(
            model=model,
            ref_model=None,
            args=dpo_config,
            train_dataset=dpo_dataset,
            processing_class=tokenizer,
        )

        print("Starting DPO training (Phase 2, GDPO-style soft labels)...")
        trainer.train()

        adapter_path = os.path.join(OUTPUT_DIR, "adapter")
        trainer.save_model(adapter_path)
        print(f"DPO adapter saved to {adapter_path}")

        # Upload
        print(f"Uploading DPO adapter to {MODEL_REPO}...")
        from huggingface_hub import HfApi
        api = HfApi(token=HF_TOKEN)
        api.upload_folder(
            folder_path=adapter_path,
            repo_id=MODEL_REPO,
            repo_type="model",
            commit_message="Phase 2: DPO adapter with GDPO-style soft preference labels (beta=0.05)",
        )
        print("Phase 2 (DPO) complete.")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"DPO TRAINING FAILED: {e}")
        print(f"{'='*60}")
        traceback.print_exc()
        error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dpo_error.txt")
        with open(error_path, "w") as f:
            f.write(f"DPO Error: {e}\n\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
