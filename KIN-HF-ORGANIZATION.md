# KIN Hugging Face Organization

## Overview

This document organizes all Hugging Face (HF) resources for the KIN (Kinetigor Cybersecurity AI) project.

**Project:** KIN - Cybersecurity AI Assistant
**Owner:** nyxspecter4
**Region:** us
**Primary Use Case:** Cybersecurity analysis, threat intelligence, vulnerability assessment

---

## Current HF Assets (4 Repos)

### Models (2)

| Repo | Type | Size | License | Status | Purpose |
|------|------|------|---------|--------|---------|
| [kinetigor-dpo-cybersec](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec) | Safetensors | 494M params | MIT | Public | Primary inference model |
| [kinetigor-dpo-cybersec-gguf](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec-gguf) | GGUF | Q4_K_M, Q8_0 | Apache 2.0 | Public | Quantized for local inference |

**Base Model:** Mistral-7B-Instruct-v0.2
**Architecture:** Qwen2
**Training:** DPO (Direct Preference Optimization)
**Training Data:** 443 unique triples

### Datasets (1)

| Repo | Type | Size | License | Visibility | Purpose |
|------|------|------|---------|------------|---------|
| [kin-cyber-all-cybersec-dpo](https://huggingface.co/datasets/nyxspecter4/kin-cyber-all-cybersec-dpo) | DPO Pairs | 443 triples | Apache 2.0 | Private | Training data |

**Data Sources:** MITRE ATT&CK, OWASP Top-10, OWASP API Top-10, NIST CSF, SANS Top-20, CIS Controls v8, Sigma rules, CVE, CISA KEV, Threat-Intel categories, ATT&CK Groups

### Spaces (1)

| Repo | SDK | Status | Purpose | URL |
|------|-----|--------|---------|-----|
| [kin-inference](https://huggingface.co/spaces/nyxspecter4/kin-inference) | Gradio 5.44.0 | RUNNING | Primary chat interface | [Open Space](https://huggingface.co/spaces/nyxspecter4/kin-inference) |

**Features:** Chat interface, cybersecurity-focused system prompt, examples

---

## Proposed Organization Structure

### Tier 1: Core (Current - All Done)
- Model: Primary inference model (safetensors)
- Model: Quantized variant (GGUF)
- Dataset: Training data (private)
- Space: Primary demo

### Tier 2: Evaluation & Testing
- Dataset: Public evaluation dataset (kin-eval-cybersec)
- Space: Evaluation dashboard
- Space: Model comparison

### Tier 3: Documentation & Discovery
- Docs: Usage documentation
- Collection: KIN Cybersecurity Ecosystem
- Collection: Best Cybersecurity LLMs

### Tier 4: Storage & Archives
- Buckets: Model backups
- Buckets: Training run artifacts

---

## Relationship Map

Training Dataset (PRIVATE) -> Primary Model (PUBLIC) -> GGUF Model (PUBLIC)
                                         -> Inference Space (PUBLIC, RUNNING)

---

## Asset Inventory

### Models

#### 1. kinetigor-dpo-cybersec
- ID: nyxspecter4/kinetigor-dpo-cybersec
- Type: Model (safetensors)
- Architecture: Qwen2
- Base: Mistral-7B-Instruct-v0.2
- Parameters: 494M
- Task: text-generation
- License: MIT
- Demo Spaces: kinetigor-dpo-cybersec-space, kin-inference
- Status: Public, Active

#### 2. kinetigor-dpo-cybersec-gguf
- ID: nyxspecter4/kinetigor-dpo-cybersec-gguf
- Type: Model (GGUF)
- Base: nyxspecter4/kinetigor-dpo-cybersec
- Quantizations: Q4_K_M (~398MB), Q8_0 (~531MB)
- Task: text-generation
- Library: gguf
- License: Apache 2.0
- Status: Public, Active

### Datasets

#### 1. kin-cyber-all-cybersec-dpo
- ID: nyxspecter4/kin-cyber-all-cybersec-dpo
- Type: Dataset
- Format: JSON (DPO triples)
- Size: 443 unique triples
- License: Apache 2.0
- Visibility: Private
- Task Categories: text-generation
- Status: Active

### Spaces

#### 1. kin-inference
- ID: nyxspecter4/kin-inference
- Type: Space
- SDK: Gradio
- SDK Version: 5.44.0
- Python Version: 3.13
- App File: app.py
- Status: RUNNING
- URL: https://huggingface.co/spaces/nyxspecter4/kin-inference

---

## Recommended Actions

### Immediate
1. Create public evaluation dataset - For benchmarking and testing
2. Update model cards - Add links to all related repos
3. Create collection - KIN Cybersecurity Ecosystem to group all assets

### Short Term
4. Add evaluation Space - Interactive benchmarking dashboard
5. Create documentation - Usage guides, API docs
6. Set up monitoring - Track downloads, likes, usage

### Long Term
7. Create buckets - For model backups and large artifacts
8. Add more Spaces - Specialized interfaces
9. Publish paper - Document methodology and results

---

## Tagging Strategy

### Consistency Rules
- All repos: region:us
- Cybersecurity: cybersec, cyber-defense, security-analyst
- Model-specific: text-generation, en
- Framework tags: mitre-attack, owasp, nist-csf, etc.

### License Tags
- Models: license:mit or license:apache-2.0
- Datasets: license:apache-2.0

---

## Quick Links

### Models
- [kinetigor-dpo-cybersec](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec)
- [kinetigor-dpo-cybersec-gguf](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec-gguf)

### Datasets
- [kin-cyber-all-cybersec-dpo](https://huggingface.co/datasets/nyxspecter4/kin-cyber-all-cybersec-dpo) (Private)

### Spaces
- [kin-inference](https://huggingface.co/spaces/nyxspecter4/kin-inference) (RUNNING)

### GitHub
- [bountywarz-ops](https://github.com/NyxSpecter4/bountywarz-ops)

---

## Maintenance Checklist

- Update model cards with related repo links
- Add evaluation dataset (public)
- Create collection for all KIN assets
- Set up CI/CD for model updates
- Add monitoring/alerts for HF repos
- Document usage examples
- Create API documentation

---

*Last updated: September 2, 2026*
*Owner: nyxspecter4 / Kinetigor*
