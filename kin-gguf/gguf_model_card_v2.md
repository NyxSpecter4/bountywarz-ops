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
  - qwen
---

# KIN -- Cybersecurity AI (GGUF)

> The most opinionated cybersecurity AI that runs on your laptop.

GGUF quantizations of [KIN](https://huggingface.co/nyxspecter4/kin-sft-lora), a cybersecurity fine-tune of Qwen2.5-3B-Instruct. Run locally with Ollama, llama.cpp, or any GGUF-compatible runtime.

## Why KIN?

KIN answers security questions like a **senior engineer at a bar** -- direct, opinionated, and specific. It names real tools (CrowdStrike Falcon, Velociraptor, Duo MFA, KnowBe4), references real CVEs (CVE-2024-3094, CVE-2021-44228, CVE-2023-4863), and knows real incidents (MGM, Colonial Pipeline, NotPetya, Maersk $300M, Merck $670M).

No hedging. No "As an AI..." Just sharp, actionable security intelligence.

## Available Quantizations

| File | Quant | Size | Use Case |
|------|-------|------|----------|
| `kin-sft-lora-Q4_K_M.gguf` | Q4_K_M | ~2.0 GB | Best balance -- recommended for most users |
| `kin-sft-lora-Q8_0.gguf` | Q8_0 | ~3.3 GB | Highest quality, near-lossless |

## Quick Start -- Ollama

    ollama run hf.co/nyxspecter4/kin-sft-lora-gguf:Q4_K_M

## Quick Start -- llama.cpp

    git clone https://github.com/ggml-org/llama.cpp
    cd llama.cpp && make
    ./llama-cli -m kin-sft-lora-Q4_K_M.gguf \
      -p "How do I detect a foothold after a phishing attack?" \
      --system-prompt "You are KIN -- a sharp cybersecurity AI partner."

## Quick Start -- Python (llama-cpp-python)

    pip install llama-cpp-python huggingface_hub
    python -c "
    from huggingface_hub import hf_hub_download
    from llama_cpp import Llama
    path = hf_hub_download('nyxspecter4/kin-sft-lora-gguf', 'kin-sft-lora-Q4_K_M.gguf')
    llm = Llama(model_path=path, n_ctx=4096, n_threads=4)
    r = llm.create_chat_completion(messages=[
        {'role': 'system', 'content': 'You are KIN -- a sharp cybersecurity AI partner.'},
        {'role': 'user', 'content': 'How do I harden SSH?'}
    ])
    print(r['choices'][0]['message']['content'])
    "

## Critical: System Prompt

KIN was trained with a specific system prompt. Using a different prompt will degrade quality significantly.

> You are KIN -- a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. No "As a cybersecurity AI expert." Name products: "CrowdStrike Falcon" not "use EDR". "Duo push MFA" not "implement MFA".

## Comparison with Similar Models

| Model | Base | Size | Downloads | Training Pairs | Runs on Laptop | GGUF |
|-------|------|------|-----------|----------------|----------------|------|
| **KIN** | Qwen2.5-3B | 2-3 GB | Growing | 550+ DPO | Yes (2GB RAM) | Yes |
| Mohamedabul/Qwen2.5-3B-CyberSecurity | Qwen2.5-3B | 6 GB | 3.5K | 187K | Needs 8GB+ | No |
| AlicanKiraz0/Cybersecurity-BaronLLM | Qwen3.6-35B | 70+ GB | 11.5K | N/A | No | No |
| RichardErkhov/Lily-Cybersecurity-GGUF | Mistral-7B | 4-5 GB | 5.2K | 22K | Yes (4GB) | Yes |

### KIN advantages

- **Runs on any laptop** -- 2GB RAM for Q4_K_M, no GPU needed
- **Ollama-ready** out of the box
- **Opinionated, specific responses** -- names tools, CVEs, and incidents
- **DPO-trained** -- chosen responses are sharp, rejected responses are vague (anti-pattern training)

## Training Data

[nyxspecter4/kin-cyber-dpo-v2](https://huggingface.co/datasets/nyxspecter4/kin-cyber-dpo-v2) -- 550+ cybersecurity DPO pairs with chosen (sharp, specific) and rejected (vague, hedging) responses.

## Live Demo

Try KIN in your browser: [nyxspecter4/kin-cybersec](https://huggingface.co/spaces/nyxspecter4/kin-cybersec)

## License

Apache 2.0
