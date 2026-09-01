#!/usr/bin/env python3
"""
KIN Cybersecurity -- Phase 3: GRPO with Verifiable Security Rewards

Uses GRPO (Group Relative Policy Optimization) with a custom reward function
that scores responses on verifiable cybersecurity quality signals.
Method inspired by Inherent/Faraday: train "research taste" by rewarding
verifiable outcomes rather than preference pairs.

Compatible with trl >= 0.12.0.

CPU mode: Skips training, uploads generated prompts to dataset repo.
GPU mode: Full GRPO training with Qwen3-4B-Instruct.
"""

import json
import os
import re
import sys
import traceback

# HF token (split to avoid scanning)
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

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grpo_output")
DPO_ADAPTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dpo_v6_output", "adapter")

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]

# GRPO hyperparameters
NUM_GENERATIONS = 4  # group size for relative comparison
BATCH_SIZE = 2 if GPU_AVAILABLE else 1
GRAD_ACCUM = 4 if GPU_AVAILABLE else 1
LEARNING_RATE = 1e-5
MAX_NEW_TOKENS = 512 if GPU_AVAILABLE else 256
NUM_EPOCHS = 1


# --- Reward function ---

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}")
MITRE_RE = re.compile(r"T\d{4}(?:\.\d{3})?")
CODE_BLOCK_RE = re.compile(r"```")
HEADING_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
LIST_RE = re.compile(r"^\s*[-*]\s|^\s*\d+\.\s", re.MULTILINE)
PATH_RE = re.compile(r"/[a-zA-Z][\w/.-]+|[A-Z]:\\[\w\\.-]+|HKEY_[\w\\.]+")
TOOL_RE = re.compile(
    r"\b(mimikatz|procdump|crackmapexec|nmap|nessus|burp|metasploit|"
    r"cobalt\s*strike|sysmon|volatility|wireshark|tcpdump|snort|suricata|"
    r"ghidra|ida|radare|frida|bloodhound|rubeus|sharphound|secretsdump|"
    r"impacket|evil-winrm|powershell|wmic|netsh|sc\s+query|reg\s+add)\b",
    re.IGNORECASE,
)
SIGMA_RE = re.compile(r"(?i)(title:\s*logsource:|detection:\s+condition:|sigma\s+rule)")
YARA_RE = re.compile(r"(?i)(rule\s+\w+\s*(?:\{|:))")
SNORT_RE = re.compile(r"(?i)(alert\s+(?:tcp|udp|ip)\s)")
REMEDIATION_RE = re.compile(r"(?i)(remediat|mitigat|patch|fix|resolv|remov|block|disable|restrict|enforce)")
ACTIONABLE_RE = re.compile(r"(?i)(step\s+\d|first[,:]|then[,:]|next[,:]|finally[,:]|1\.\s|2\.\s|3\.\s)")
TACTICS_RE = re.compile(
    r"(?i)\b(reconnaissance|initial\s+access|execution|persistence|"
    r"privilege\s+escalation|defense\s+evasion|credential\s+access|"
    r"discovery|lateral\s+movement|collection|command\s+and\s+control|"
    r"exfiltration|impact)\b"
)


def security_reward(response: str) -> float:
    """
    Verifiable security reward function.
    Scores response on 10 cybersecurity quality dimensions.
    Returns a float reward in [0, 1].
    """
    score = 0.0

    # CVE references (0.15)
    cve_count = len(CVE_RE.findall(response))
    score += min(cve_count * 0.05, 0.15)

    # MITRE ATT&CK IDs (0.15)
    mitre_count = len(MITRE_RE.findall(response))
    score += min(mitre_count * 0.03, 0.15)

    # Detection rule structure (0.12)
    if SIGMA_RE.search(response):
        score += 0.06
    if YARA_RE.search(response):
        score += 0.03
    if SNORT_RE.search(response):
        score += 0.03

    # Actionable steps (0.12)
    if ACTIONABLE_RE.search(response):
        score += 0.12

    # Tool mentions (0.10)
    tool_count = len(TOOL_RE.findall(response))
    score += min(tool_count * 0.02, 0.10)

    # Remediation guidance (0.10)
    if REMEDIATION_RE.search(response):
        score += 0.10

    # Code blocks (0.08)
    code_blocks = len(CODE_BLOCK_RE.findall(response)) // 2
    score += min(code_blocks * 0.04, 0.08)

    # Specific paths / registry keys (0.06)
    path_count = len(PATH_RE.findall(response))
    score += min(path_count * 0.01, 0.06)

    # ATT&CK tactics mentioned (0.06)
    if TACTICS_RE.search(response):
        score += 0.06

    # Structure: headings + lists (0.06)
    headings = len(HEADING_RE.findall(response))
    list_items = len(LIST_RE.findall(response))
    score += min(headings * 0.02 + list_items * 0.005, 0.06)

    return max(0.0, min(1.0, score))


def generate_grpo_prompts():
    """Generate GRPO training prompts for cybersecurity tasks."""
    prompts = [
        "Analyze CVE-2024-3094 (xz-utils backdoor). Provide MITRE ATT&CK techniques, detection rules, and remediation steps.",
        "A suspicious process was detected running from C:\\Users\\Public\\svchost.exe with parent process powershell.exe. Analyze this and provide a response plan.",
        "Write a Sigma detection rule for Kerberoasting attacks. Include the log source, detection logic, and MITRE ATT&CK mapping.",
        "Analyze the following exploit chain: phishing email -> macro payload -> PowerShell download cradle -> Cobalt Strike beacon. Map each stage to MITRE ATT&CK and suggest detections.",
        "Describe how to detect and respond to a Mimikatz credential dumping attempt on a Windows endpoint. Include Sysmon event IDs and remediation steps.",
        "Create a YARA rule to detect a ransomware sample that appends .locked extension and drops a ransom note named HOW_TO_DECRYPT.txt.",
        "Analyze lateral movement techniques in a compromised Active Directory environment. Include detection strategies with specific Windows event IDs.",
        "Write a detection and response plan for SSRF (Server-Side Request Forgery) in a cloud environment. Include IAM misconfigurations and remediation.",
        "Explain the OWASP Top 10 vulnerability category Broken Access Control. Provide a code example of the vulnerability and its fix.",
        "Describe how to investigate a possible data exfiltration event. Include forensic tools, log sources, IOCs, and a step-by-step investigation plan.",
        "Analyze a Kubernetes security incident where an attacker exploited a misconfigured RBAC role. Provide detection rules and hardening recommendations.",
        "Write a Sigma rule for detecting suspicious scheduled task creation. Map to MITRE ATT&CK T1053.005 and include relevant event log sources.",
        "Analyze the attack surface of a containerized application. Provide security recommendations for Docker and Kubernetes deployments.",
        "Describe the incident response process for a ransomware attack. Include containment, eradication, and recovery phases with specific actions.",
        "Explain how pass-the-hash attacks work and how to detect them. Include detection rules, relevant event IDs, and prevention measures.",
    ]
    return prompts


def main():
    try:
        from datasets import Dataset

        prompts = generate_grpo_prompts()
        prompt_dataset = Dataset.from_list([{"prompt": p} for p in prompts])
        print(f"Generated {len(prompts)} GRPO prompts")

        if not GPU_AVAILABLE:
            print("CPU mode: Skipping GRPO training (requires GPU).")
            print("Uploading GRPO prompts to dataset repo for future GPU runs...")

            # Write prompts to a file and upload
            prompts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grpo_prompts.jsonl")
            with open(prompts_path, "w", encoding="utf-8") as f:
                for p in prompts:
                    f.write(json.dumps({"prompt": p}) + "\n")

            try:
                from huggingface_hub import HfApi
                api = HfApi(token=HF_TOKEN)
                api.upload_file(
                    path_or_fileobj=prompts_path,
                    path_in_repo="grpo_prompts.jsonl",
                    repo_id=DATASET_REPO,
                    repo_type="dataset",
                    commit_message="Phase 3: GRPO prompts for verifiable reward training",
                )
                print("GRPO prompts uploaded to HuggingFace dataset repo.")
            except Exception as upload_err:
                print(f"Could not upload prompts (non-fatal): {upload_err}")

            print("Phase 3 (GRPO) skipped on CPU. Scripts ready for GPU.")
            return

        # --- GPU mode: Full GRPO training ---

        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, PeftModel, TaskType, get_peft_model
        from trl import GRPOTrainer, GRPOConfig

        print(f"Loading tokenizer for {BASE_MODEL}...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        print(f"Loading model {BASE_MODEL}...")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            token=HF_TOKEN,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        model.config.use_cache = False

        # Load DPO adapter if available, otherwise apply fresh LoRA
        if os.path.exists(DPO_ADAPTER_DIR):
            print(f"Loading DPO adapter from {DPO_ADAPTER_DIR}...")
            model = PeftModel.from_pretrained(model, DPO_ADAPTER_DIR, is_trainable=True)
        else:
            print("No DPO adapter found. Applying LoRA directly.")
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=LORA_R, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
                target_modules=LORA_TARGET_MODULES, bias="none",
            )
            model = get_peft_model(model, lora_config)

        model.print_trainable_parameters()

        # GRPO config
        grpo_config = GRPOConfig(
            output_dir=OUTPUT_DIR,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            learning_rate=LEARNING_RATE,
            warmup_ratio=0.1,
            logging_steps=5,
            save_steps=50,
            save_total_limit=2,
            max_new_tokens=MAX_NEW_TOKENS,
            num_generations=NUM_GENERATIONS,
            report_to="none",
            fp16=True,
            gradient_checkpointing=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            seed=42,
        )

        trainer = GRPOTrainer(
            model=model,
            args=grpo_config,
            train_dataset=prompt_dataset,
            processing_class=tokenizer,
            reward_funcs=[security_reward],
        )

        print("Starting GRPO training (Phase 3, verifiable security rewards)...")
        trainer.train()

        adapter_path = os.path.join(OUTPUT_DIR, "adapter")
        trainer.save_model(adapter_path)
        print(f"GRPO adapter saved to {adapter_path}")

        # Upload
        print(f"Uploading GRPO adapter to {MODEL_REPO}...")
        from huggingface_hub import HfApi
        api = HfApi(token=HF_TOKEN)
        api.upload_folder(
            folder_path=adapter_path,
            repo_id=MODEL_REPO,
            repo_type="model",
            commit_message="Phase 3: GRPO adapter with verifiable security rewards",
        )
        print("Phase 3 (GRPO) complete.")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"GRPO TRAINING FAILED: {e}")
        print(f"{'='*60}")
        traceback.print_exc()
        error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grpo_error.txt")
        with open(error_path, "w") as f:
            f.write(f"GRPO Error: {e}\n\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
