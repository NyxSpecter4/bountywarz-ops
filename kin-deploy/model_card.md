---
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
    {"role": "system", "content": "You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. Open with your take, not your title. No 'As a cybersecurity AI expert.' Name products: 'CrowdStrike Falcon' not 'use EDR'. 'Duo push MFA' not 'implement MFA'."},
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

Try KIN at [kin-inference Space](https://huggingface.co/spaces/nyxspecter4/kin-inference).

## Limitations

- **3B model**: Less factual knowledge than larger models. Always verify named CVEs and tool recommendations.
- **Opinionated voice**: KIN gives bold takes. Verify before acting.
- **Not a substitute** for professional security advice.

## License

Apache 2.0
