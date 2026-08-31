---
license: apache-2.0
language:
  - en
base_model: nyxspecter4/kin-sft-lora
library_name: gguf
pipeline_tag: text-generation
tags:
  - cybersecurity
  - security
  - gguf
  - ollama
  - llama-cpp
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

# KIN — Cybersecurity AI (GGUF)

GGUF quantizations of [KIN](https://huggingface.co/nyxspecter4/kin-sft-lora), a cybersecurity fine-tune of Qwen2.5-3B-Instruct. Run locally with Ollama, llama.cpp, or any GGUF-compatible runtime.

## Available Quantizations

| File | Quant | Size | Use Case |
|------|-------|------|----------|
| `kin-sft-lora-Q4_K_M.gguf` | Q4_K_M | ~2.0 GB | Best balance — recommended for most users |
| `kin-sft-lora-Q8_0.gguf` | Q8_0 | ~3.3 GB | Highest quality, near-lossless |

## Quick Start — Ollama

```bash
# Pull and run directly from Hugging Face
ollama run hf.co/nyxspecter4/kin-sft-lora-gguf:Q4_K_M

# Or pull the Q8_0 version
ollama run hf.co/nyxspecter4/kin-sft-lora-gguf:Q8_0
```

## Quick Start — llama.cpp

```bash
# Build llama.cpp
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && make

# Run KIN
./llama-cli -m kin-sft-lora-Q4_K_M.gguf \
  -p "How do I detect a foothold after a phishing attack?" \
  --system-prompt "You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook."
```

## Critical: System Prompt

KIN was trained with a specific system prompt. Using a different prompt will degrade quality significantly.

> You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. Open with your take, not your title. No "As a cybersecurity AI expert." Name products: "CrowdStrike Falcon" not "use EDR". "Duo push MFA" not "implement MFA".

## About KIN

KIN answers security questions like a **senior engineer at a bar** — direct, opinionated, and specific. It names real tools (CrowdStrike Falcon, Velociraptor, Duo MFA, KnowBe4), references real CVEs (CVE-2023-4863, CVE-2021-44228, CVE-2024-3094), and knows real incidents (MGM, Colonial Pipeline, NotPetya, Maersk $300M, Merck $670M).

## Training Data

Training data available at [nyxspecter4/kin-dpo-data](https://huggingface.co/datasets/nyxspecter4/kin-dpo-data).

## License

Apache 2.0
