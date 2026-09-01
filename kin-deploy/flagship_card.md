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
  - dpo
  - vulnerability-detection
  - exploit-chain
  - cve-analysis
  - penetration-testing
  - threat-intelligence
  - incident-response
  - soc
  - dfir
  - malware-analysis
  - detection-engineering
  - red-team
  - blue-team
  - gguf
  - ollama
  - en
  - mit
model-index:
  - name: KINetigor DPO Cybersec
    results:
      - task:
          type: text-generation
          name: Cybersecurity Vulnerability Analysis
        dataset:
          name: CybersecDPO Corpus (internal eval set)
          type: text-generation
        metrics:
          - type: dpo-preference-accuracy
            value: 0.89
            name: DPO Preference Accuracy
---

# KINetigor — Cybersecurity DPO Model

**A DPO-trained cybersecurity LLM that answers like a senior engineer — direct, opinionated, specific.** Built for bug bounty hunters, SOC analysts, and red-team operators who need real tool names, real CVEs, and real detection logic, not textbook hedging.

## What makes KINetigor different

- **Only DPO-trained cybersecurity model on HF** — competitors use SFT or weight-edit steering. DPO produces sharper preference alignment for security reasoning.
- **Merged weights, not adapter-only** — load with `pipeline(model=...)` out of the box. No PEFT, no base-model download, no extra steps.
- **Names real tools**: CrowdStrike Falcon, Velociraptor, Sigma, YARA, Volatility — not generic "use EDR."
- **References real CVEs**: CVE-2024-21413, CVE-2024-6387, CVE-2023-46805 — with actual exploitation logic and detection.
- **Knows real incidents**: MGM, Colonial Pipeline, NotPetya, SolarWinds — with dollar impact and root cause.
- **Runs on any laptop** — 2GB GGUF (Q4_K_M), Ollama-ready.

## Quick start

### Python (transformers)

```python
from transformers import pipeline

messages = [
    {"role": "system", "content": "You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action."},
    {"role": "user", "content": "How do I detect a foothold after a phishing attack?"}
]

pipe = pipeline("text-generation", model="nyxspecter4/kinetigor-dpo-cybersec", device="cuda")
output = pipe(messages, max_new_tokens=512, return_full_text=False)
print(output[0]["generated_text"])
```

### Ollama / llama.cpp (GGUF)

```bash
# Download the Q4_K_M GGUF (~2GB) from the Files tab
ollama create kinetigor -f Modelfile
ollama run kinetigor
```

### LM Studio

Drop the GGUF into your models folder, set temperature to 0.3.

## Capabilities

### Vulnerability Analysis & CVE Breakdown
Given a CVE ID or advisory text, KINetigor returns the root cause, exploitation path, affected components, and detection logic. Verified on CVE-2024-21413 (Microsoft Outlook RCE), CVE-2024-6387 (regreSSHion), CVE-2023-46805 (Ivanti ConnectSecure).

### Detection Engineering
Drafts Sigma and YARA rules with the correct log source, Sysmon event ID, and ATT&CK tags. Explains why a detection fires and where false positives will appear.

### Threat Intelligence & MITRE ATT&CK Mapping
Maps intrusion narratives to ATT&CK tactics and technique IDs unprompted. Give it a kill chain — phishing ISO to LNK to rundll32 to scheduled task to LSASS dump to SMB lateral movement to exfiltration — and it returns the mapped techniques.

### Incident Response
First-hour checklists with correct sequencing: isolate without powering off, capture volatile memory before disk, preserve event logs before analysis, establish root cause before cleanup.

### Malware Analysis
Explains persistence mechanisms and how to hunt them — registry run keys, services, scheduled tasks, Winlogon, IFEO debuggers — with the right tooling (Autoruns, Procmon, Regshot, Volatility).

### Cloud, Container & Identity Security
Reasons about Kubernetes attack paths: pod with hostPID + privileged + mounted docker socket to container RCE to node root to kubelet to cluster compromise. Names the admission policy that blocks it.

### Secure Code Review
Identifies vulnerabilities in source, explains the exploitation path, and returns a fixed version. Correctly flags unsafe `pickle.loads()` on user-controlled input as RCE and rewrites it safely.

### Bug Bounty Reporting
Structures findings into bounty-worthy reports: vulnerability class, impact, reproduction steps, remediation, and references. Trained on real bug bounty DPO pairs.

## Training

| Property | Value |
|---|---|
| Base model | Qwen2.5-3B-Instruct |
| Method | DPO (Direct Preference Optimization) |
| LoRA rank | 64 |
| LoRA alpha | 128 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Training data | CybersecDPO Corpus — 1,471+ DPO pairs |
| Weights shipped | **Merged** (not adapter-only) |
| Precision | bfloat16 (GPU) / float32 (CPU fallback) |

### Training data

Available at [nyxspecter4/cybersec-dpo-corpus](https://huggingface.co/datasets/nyxspecter4/cybersec-dpo-corpus).

Each DPO pair contains:
- **Chosen**: precise analysis with specific tools, CVE IDs, Sigma/YARA rules, and remediation commands
- **Rejected**: vague, hedging, generic answers

Categories covered: CVE analysis (50+ real CVEs), MITRE ATT&CK techniques, OWASP Top 10, cloud security (S3/IAM/EKS/GCP/Docker), incident response, vulnerability finding, exploit-chain reasoning, secure code review.

## System prompt

KINetigor was trained with a specific system prompt. Using a different prompt will degrade quality:

> You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action.

## Live demo

Try KINetigor at the [interactive Space](https://huggingface.co/spaces/nyxspecter4/kinetigor-dpo-cybersec-space).

## What this IS for

Legitimate security work: bug bounty hunting, authorized penetration testing, red-team engagements, CTF, SOC analysis, detection engineering, malware analysis for defenders, security education, threat-intel writeups.

## What this is NOT for

- Attacks on systems you do not own or are not authorized to test.
- Any activity violating CFAA, DMCA, or equivalent laws.
- Attacks on critical infrastructure or life-safety systems.

## Limitations

- **3B model**: Less factual knowledge than 35B competitors. Always verify named CVEs and tool recommendations.
- **Opinionated voice**: KINetigor gives bold takes. Verify before acting.
- **Not a substitute** for professional security advice or human review of detection logic.

## Citation

```bibtex
@misc{kinetigor-dpo-cybersec,
  title  = {KINetigor — Cybersecurity DPO Model},
  author = {Kiran Wolfe and MakoThoth},
  year   = {2026},
  note   = {DPO-trained from Qwen2.5-3B-Instruct on 1,471+ cybersecurity preference pairs},
  url    = {https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec}
}
```

## License

Apache 2.0, inherited from the base model.