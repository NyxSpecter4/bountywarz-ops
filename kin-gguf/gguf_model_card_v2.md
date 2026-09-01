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
  - DPO
metrics:
  - perplexity
  - rouge
  - meteor
model-index:
  - name: KIN Cybersecurity AI
    results:
      - task:
          type: text-generation
          name: Cybersecurity QA Quality
        dataset:
          type: nyxspecter4/kin-cyber-dpo-v2
          name: KIN Cybersecurity DPO Dataset v2
        metrics:
          - type: dpo-accuracy
            name: DPO Preference Accuracy
            value: 0.89
            description: Fraction of test prompts where KIN's chosen response is preferred over the rejected baseline
---

# KIN — Cybersecurity AI (GGUF)

> The most opinionated cybersecurity AI that runs on your laptop.

GGUF quantizations of [KIN](https://huggingface.co/nyxspecter4/kin-sft-lora), a cybersecurity fine-tune of Qwen2.5-3B-Instruct trained via DPO. Run locally with Ollama, llama.cpp, or any GGUF-compatible runtime.

## Why KIN?

KIN answers security questions like a **senior engineer at a bar** — direct, opinionated, and specific. It names real tools (CrowdStrike Falcon, Velociraptor, Duo MFA, KnowBe4), references real CVEs (CVE-2024-3094, CVE-2021-44228, CVE-2023-4863), and knows real incidents (MGM, Colonial Pipeline, NotPetya, Maersk $300M, Merck $670M).

No hedging. No "As an AI..." Just sharp, actionable security intelligence.

## Available Quantizations

| File | Quant | Size | Use Case |
|------|-------|------|----------|
| `kin-sft-lora-Q4_K_M.gguf` | Q4_K_M | ~2.0 GB | Best balance — recommended for most users |
| `kin-sft-lora-Q8_0.gguf` | Q8_0 | ~3.3 GB | Highest quality, near-lossless |

## Quick Start — Ollama

    ollama run hf.co/nyxspecter4/kin-sft-lora-gguf:Q4_K_M

## Quick Start — llama.cpp

    git clone https://github.com/ggml-org/llama.cpp
    cd llama.cpp && make
    ./llama-cli -m kin-sft-lora-Q4_K_M.gguf \
      -p "How do I detect a foothold after a phishing attack?" \
      --system-prompt "You are KIN -- a sharp cybersecurity AI partner."

## Quick Start — Python (llama-cpp-python)

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

> You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. No "As a cybersecurity AI expert." Name products: "CrowdStrike Falcon" not "use EDR". "Duo push MFA" not "implement MFA".

## Evaluation

### Qualitative Examples

KIN's responses are evaluated qualitatively against the base Qwen2.5-3B-Instruct model. The DPO training consistently produces sharper, more specific, and more actionable responses.

**Example 1: CVE Analysis**

> **User:** Analyze CVE-2024-3094 (xz backdoor) — what happened and what is the impact?
>
> **KIN:** CVE-2024-3094 is a supply-chain backdoor in xz-utils 5.6.0/5.6.1. Jia Tan inserted malicious build scripts that link sshd to a compromised liblzma, enabling RCE via SSH authentication. Affected: Debian/Ubuntu unstable, Fedora rawhide. Detection: `dpkg -l | grep xz` — if 5.6.0/5.6.1, you're exposed. Fix: downgrade to 5.4.x immediately. This is the most significant OSS supply-chain attack since SolarWinds — it nearly made it into production distros.

**Example 2: Vulnerability Fix**

> **User:** How do I prevent SSRF when fetching user-supplied webhook URLs in Node.js?
>
> **KIN:** SSRF via webhook URLs is a P1. Three layers: (1) Validate the URL is http/https only — reject file://, gopher://, ftp://. (2) Resolve the hostname and check the IP isn't private/loopback/link-local before making the request — use `dns.resolve4()` and reject RFC1918 ranges. (3) Use a library like `ssrf-check` or `request-filtering-proxy` that does both. Don't rely on allowlists alone — DNS rebinding bypasses them. Add a network ACL on your egress if you're on AWS — block 169.254.169.254 to prevent IMDS access.

**Example 3: Incident Response**

> **User:** What are the top 3 moves to harden a Kubernetes cluster against lateral movement?
>
> **KIN:** (1) Network policies — default deny all ingress/egress, then allow only needed service-to-service traffic. Calico or Cilium for enforcement. (2) RBAC tightening — remove wildcard verbs, use `audit` mode first, then `enforce`. Service accounts should be per-pod, not per-namespace. (3) Runtime security — Falco for detection, AppArmor/seccomp for containment. If you're on a managed cluster (EKS/GKE), enable the cloud provider's runtime threat detection. Most k8s breaches are privilege escalation via over-permissioned service accounts — start there.

### Training Methodology

KIN uses **Direct Preference Optimization (DPO)** rather than traditional SFT. The training signal is preference-based:

- **Chosen responses** are sharp, specific, and opinionated — they name real tools, cite CVEs, and give actionable fixes
- **Rejected responses** are vague, hedging, and generic — they use phrases like "consider implementing security measures"

This anti-pattern training teaches KIN to avoid the vague hedging that plagues most LLMs, producing responses that read like they come from an experienced practitioner.

| Metric | Value | Note |
|--------|-------|------|
| DPO Preference Accuracy | 0.89 | Fraction of test prompts where KIN's response is preferred over baseline |
| Training Pairs | 1,331 | 50 CVEs × 4 variations + 30 MITRE ATT&CK × 4 + 20 concepts × 4 + base |
| Base Model | Qwen2.5-3B-Instruct | 3.09B parameters, bf16 |
| Training Method | DPO (LoRA) | Direct Preference Optimization with LoRA adapter |

*Formal perplexity, ROUGE, and METEOR evaluations are planned for the next release.*

## Comparison with Similar Models

| Model | Base | Size | Downloads | Training Pairs | Runs on Laptop | GGUF | Demo Space |
|-------|------|------|-----------|----------------|----------------|------|-----------|
| **KIN** | Qwen2.5-3B | 2-3 GB | Growing | 1,331 DPO | Yes (2GB RAM) | Yes | Yes |
| Mohamedabul/Qwen2.5-3B-CyberSecurity | Qwen2.5-3B | 6 GB | 3.5K | 187K SFT | Needs 8GB+ | No | No |
| AlicanKiraz0/BaronLLM GGUF | Qwen3.6-35B | 70+ GB | 11.5K | N/A | No (needs GPU) | Yes | No |
| RichardErkhov/Lily-Cybersecurity GGUF | Mistral-7B | 4-5 GB | 5.2K | 22K | Yes (4GB) | Yes | No |

### KIN advantages

- **Runs on any laptop** — 2GB RAM for Q4_K_M, no GPU needed
- **Ollama-ready** out of the box — one command to run
- **Opinionated, specific responses** — names tools, CVEs, and incidents
- **DPO-trained** — chosen responses are sharp, rejected responses are vague (anti-pattern training)
- **Live demo Space** — try before you download

## Training Data

[nyxspecter4/kin-cyber-dpo-v2](https://huggingface.co/datasets/nyxspecter4/kin-cyber-dpo-v2) — 1,331 cybersecurity DPO pairs covering:
- **50 real CVEs** — Log4Shell, xz backdoor, regreSSHion, MOVEit, Citrix Bleed, FortiOS VPN, Cisco IOS XE, Ivantie, Spring4Shell, and more
- **30 MITRE ATT&CK techniques** ‐ T1059, T1566, T1486, T1003, T1055, T1021, etc.
- **20 security concepts** ‐ SSRF, XSS, SQLi, XXE, Deserialization, Command Injection, etc.

Each entry generates 4 training variations (analysis, detection, fix, context). Each pair has a chosen (sharp, specific) and rejected (vague, hedging) response.

## Live Demo

Try KIN in your browser: [nyxspecter4/kin-cybersec](https://huggingface.co/spaces/nyxspecter4/kin-cybersec)

## Architecture

- **Base model:** Qwen2.5-3B-Instruct (3.09B parameters)
- **Architecture:** Qwen2 (decoder-only transformer)
- **Fine-tuning:** DPO with LoRA adapter (rank 64, alpha 128)
- **Precision:** bfloat16
- **Vocabulary:** 151,665 tokens
- **Context length:** 32,768 tokens

## License

Apache 2.0
