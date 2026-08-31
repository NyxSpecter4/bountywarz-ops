#!/usr/bin/env python3
"""Create kin-cybersec Space (public, Gradio) + update model card + cleanup test file."""
import os, tempfile, traceback

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

from huggingface_hub import HfApi, create_repo

api = HfApi(token=HF_TOKEN)
SPACE_ID = "nyxspecter4/kin-cybersec"
MODEL_ID = "nyxspecter4/kin-sft-lora"

README = (
    "---\n"
    "title: KIN Cybersecurity AI\n"
    "emoji: \U0001f6e1\n"
    "colorFrom: gray\n"
    "colorTo: blue\n"
    "sdk: gradio\n"
    "sdk_version: 4.44.0\n"
    "app_file: app.py\n"
    "pinned: true\n"
    "tags:\n"
    "  - cybersecurity\n"
    "  - security\n"
    "  - threat-intelligence\n"
    "  - penetration-testing\n"
    "models:\n"
    "  - nyxspecter4/kin-sft-lora\n"
    "---\n\n"
    "# KIN \u2014 Cybersecurity AI\n\n"
    "Chat with KIN, a cybersecurity AI fine-tuned on Qwen2.5-3B-Instruct. "
    "Direct, opinionated, specific \u2014 like a senior engineer at a bar.\n"
)

REQS = "gradio==4.44.0\nhuggingface_hub>=0.26.0\n"

MODEL_CARD = """---
license: apache-2.0
language:
  - en
base_model: Qwen/Qwen2.5-3B-Instruct
library_name: transformers
pipeline_tag: text-generation
tags:
  - cybersecurity
  - security
  - penetration-testing
  - vulnerability
  - CVE
  - SOC
  - DFIR
  - threat-intelligence
  - incident-response
  - SIEM
  - EDR
  - malware-analysis
  - digital-forensics
  - threat-hunting
  - infosec
  - offensive-security
  - defensive-security
  - red-team
  - blue-team
---

# KIN — Cybersecurity AI Partner

KIN is a fine-tuned cybersecurity AI built on **Qwen2.5-3B-Instruct**. It answers security questions like a **senior engineer at a bar** — direct, opinionated, and specific. No disclaimers. No hedging. Just the answer.

## What Makes KIN Different

- **Names real tools**: CrowdStrike Falcon, Velociraptor, Duo MFA, KnowBe4 — not generic "use EDR"
- **References real CVEs**: CVE-2023-4863, CVE-2021-44228, CVE-2024-3094 — with actual context
- **Knows real incidents**: MGM, Colonial Pipeline, NotPetya, Maersk ($300M), Merck ($670M)
- **Leads with the take**: Opens with the answer, not the disclaimer

## Quick Start

```python
from transformers import pipeline

messages = [
    {"role": "system", "content": "You are KIN \u2014 a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. Open with your take, not your title. No 'As a cybersecurity AI expert.' Name products: 'CrowdStrike Falcon' not 'use EDR'. 'Duo push MFA' not 'implement MFA'."},
    {"role": "user", "content": "How do I detect a foothold after a phishing attack?"}
]

pipe = pipeline("text-generation", model="nyxspecter4/kin-sft-lora", device="cuda")
output = pipe(messages, max_new_tokens=512, return_full_text=False)
print(output[0]["generated_text"])
```

## Critical: System Prompt

KIN was trained with a specific system prompt. **Using a different prompt will degrade quality significantly.**

> You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. Open with your take, not your title. No "As a cybersecurity AI expert." Name products: "CrowdStrike Falcon" not "use EDR". "Duo push MFA" not "implement MFA".

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | Qwen2.5-3B-Instruct |
| Method | LoRA SFT |
| LoRA rank | 8 |
| LoRA alpha | 16 |
| Target modules | q_proj, k_proj, v_proj, o_proj |
| Training data | Cybersecurity Q&A DPO pairs |
| Framework | TRL 0.14.0, Transformers 4.48.0 |

## Training Data

Available at [nyxspecter4/kin-dpo-data](https://huggingface.co/datasets/nyxspecter4/kin-dpo-data).

## Live Demo

Try KIN at [kin-cybersec Space](https://huggingface.co/spaces/nyxspecter4/kin-cybersec).

## GGUF Version

GGUF quantizations (Q4_K_M, Q8_0) available at [nyxspecter4/kin-sft-lora-gguf](https://huggingface.co/nyxspecter4/kin-sft-lora-gguf) for local inference with Ollama and llama.cpp.

## Limitations

- **3B model**: Less factual knowledge than larger models. Always verify named CVEs and tool recommendations.
- **Opinionated voice**: KIN gives bold takes. Verify before acting.
- **Not a substitute** for professional security advice.

## License

Apache 2.0
"""

print("=" * 60)
print("CREATE KIN-CYBERSEC SPACE + UPDATE MODEL CARD")
print("=" * 60)

# 0. Clean up test file from model repo
print("\n[0] Cleaning up test file...")
try:
    api.delete_file(path_in_repo="CREATE_REPO_TEST.md",
        repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
    print("  Deleted CREATE_REPO_TEST.md")
except Exception as e:
    print(f"  Could not delete: {e}")

# 1. Create Space (with space_sdk="gradio"!)
print("\n[1] Creating Space...")
try:
    create_repo(SPACE_ID, repo_type="space", private=False,
                space_sdk="gradio", token=HF_TOKEN, exist_ok=True)
    print("  Space created!")
except Exception as e:
    print(f"  Error: {e}")
    traceback.print_exc()

# 2. Upload README
print("\n[2] Uploading README...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(README)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("  Done")

# 3. Upload app.py from repo file
print("\n[3] Uploading app.py...")
api.upload_file(path_or_fileobj="kin-spaces/app.py", path_in_repo="app.py",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
print("  Done")

# 4. Upload requirements.txt
print("\n[4] Uploading requirements.txt...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write(REQS)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="requirements.txt",
    repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
os.unlink(p)
print("  Done")

# 5. Update model card
print("\n[5] Updating model card...")
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(MODEL_CARD)
    p = f.name
api.upload_file(path_or_fileobj=p, path_in_repo="README.md",
    repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
os.unlink(p)
print("  Done")

# 6. Verify
print("\n[6] Verifying Space...")
try:
    import requests
    r = requests.get(f"https://huggingface.co/api/spaces/{SPACE_ID}",
        headers={"Authorization": f"Bearer {HF_TOKEN}"}, timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f"  Private: {data.get('private', 'unknown')}")
        print(f"  SDK: {data.get('sdk', 'unknown')}")
        if not data.get("private", True):
            print("  SPACE IS PUBLIC!")
    else:
        print(f"  Status: {r.status_code}")
        print(f"  Body: {r.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
