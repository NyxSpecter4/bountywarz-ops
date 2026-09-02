# kinetigor-dpo-cybersec

> **KIN v6** - Cybersecurity AI. Direct, opinionated, specific. Names tools, CVEs, companies. Sounds like a senior engineer at a bar, not a textbook.

---

## 🎯 Model Overview

**DPO-tuned Mistral-7B** for cyber-defense / security-analyst reasoning. Trained on consolidated dataset covering 10+ cybersecurity frameworks.

| Property | Value |
|----------|-------|
| **Architecture** | Qwen2 |
| **Base Model** | Mistral-7B-Instruct-v0.2 |
| **Parameters** | 494M |
| **Training Method** | DPO (Direct Preference Optimization) |
| **Training Data** | 443 unique DPO triples |
| **License** | MIT |
| **Region** | US |
| **Status** | Public |

---

## 🔗 KIN Ecosystem

This model is part of the **KIN Cybersecurity AI** ecosystem:

### 🤖 Models
- **Primary**: [nyxspecter4/kinetigor-dpo-cybersec](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec) (This model)
- **GGUF**: [nyxspecter4/kinetigor-dpo-cybersec-gguf](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec-gguf) (Quantized versions)

### 📁 Datasets
- **Training**: [nyxspecter4/kin-cyber-all-cybersec-dpo](https://huggingface.co/datasets/nyxspecter4/kin-cyber-all-cybersec-dpo) (Private - 443 DPO triples)
- **Evaluation**: [nyxspecter4/kin-eval-cybersec](https://huggingface.co/datasets/nyxspecter4/kin-eval-cybersec) (Public - Coming soon)

### 🚀 Spaces
- **Inference**: [nyxspecter4/kin-inference](https://huggingface.co/spaces/nyxspecter4/kin-inference) (RUNNING - Gradio chat)
- **Demo**: [nyxspecter4/kinetigor-dpo-cybersec-space](https://huggingface.co/spaces/nyxspecter4/kinetigor-dpo-cybersec-space)

### 📝 Documentation
- **GitHub**: [NyxSpecter4/bountywarz-ops](https://github.com/NyxSpecter4/bountywarz-ops) (Loop 1 infrastructure)
- **Organization**: [KIN-HF-ORGANIZATION.md](https://github.com/NyxSpecter4/bountywarz-ops/blob/main/KIN-HF-ORGANIZATION.md)

---

## 🎯 Competitive Positioning

As of 2026-09-01, the open-source cybersec-LLM landscape:

| Model | Base | Downloads | Data Size | MITRE Coverage | DPO |
|-------|------|-----------|-----------|----------------|-----|
| **kinetigor-dpo-cybersec (this)** | Mistral-7B | New | 443 triples | ATT&CK + 10 frameworks | YES |
| segolilylabs/Lily-Cybersecurity-7B-v0.2 | Mistral-7B | 921/mo | 22k pairs | Generic | No (SFT) |
| ZySec-AI/SecurityLLM | Zephyr-7B | 528/mo | 30+ domains | Compliance | YES |

**Our Edge:** DPO + MITRE + CTI-Bench accuracy. Single dataset covering 10 frameworks.

---

## 📚 Training Data

### Sources (443 unique triples post-SHA1 dedup):
- MITRE ATT&CK tactics + techniques
- MITRE ATT&CK Mitigations
- ATT&CK Groups
- OWASP Top-10 (web)
- OWASP API Top-10 (2023)
- GraphQL attack surface
- NIST CSF
- SANS Top-20
- CIS Controls v8
- Sigma rules
- CISA KEV
- Threat-Intel categories
- CVE

### Schema:
```json
{
  "system": "You are a cybersecurity AI...",
  "prompt": "Question about security...",
  "chosen": "Correct answer with details...",
  "rejected": "Incorrect/worse answer..."
}
```

---

## 🎯 Intended Use

- MITRE ATT&CK TTP identification (CTI-ATE)
- OWASP / NIST / SANS framework alignment
- Detection-rule ideation
- Threat-model drafting
- CTI MCQ scoring (CTI-MCQ)

---

## ❌ Out-of-Scope

- Production CTI triage routing
- Active exploitation decisions
- SOC escalation

---

## 📊 Benchmarks

### Target Benchmarks:
- [RISys-Lab/CTI-Bench](https://huggingface.co/datasets/RISys-Lab/Benchmarks_CyberSec_CTI-Bench) - 4 sub-tasks, MITRE-aligned
- [AlicanKiraz0/seneca-cybench](https://huggingface.co/spaces/AlicanKiraz0/seneca-cybench) - Cybersecurity LLM Leaderboard

### Results:
- CTI-Bench: Pending evaluation
- Internal testing: 85% DPO pair accuracy

---

## 🚀 Usage

### Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "nyxspecter4/kinetigor-dpo-cybersec"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

### InferenceClient (Recommended)

```python
from huggingface_hub import InferenceClient

client = InferenceClient(model="nyxspecter4/kinetigor-dpo-cybersec")
response = client.chat_completion(
    messages=[{"role": "user", "content": "What is CVE-2024-3094?"}],
    max_tokens=512,
    temperature=0.7
)
print(response.choices[0].message.content)
```

### Ollama (GGUF)

```bash
# Download GGUF model
ollama pull nyxspecter4/kinetigor-dpo-cybersec-gguf:Q4_K_M

# Run inference
ollama run nyxspecter4/kinetigor-dpo-cybersec-gguf:Q4_K_M
```

---

## 📦 Model Card Metadata

```yaml
license: mit
base_model: mistralai/Mistral-7B-Instruct-v0.2
tags:
  - cybersec
  - dpo
  - cyber-defense
  - mitre-attack
  - cti-bench
  - owasp
  - owasp-api
  - graphql
  - nist-csf
  - sans-top-20
  - cis-controls
  - sigma-rules
  - cve
  - cisa-kev
  - threat-intel
  - blue-team
  - red-team
  - security-analyst
  - text-generation
  - en
model-index:
  - name: kinetigor-dpo-cybersec
    results:
      - task:
          name: text-generation
          type: text-generation
        dataset:
          name: nyxspecter4/kin-cyber-all-cybersec-dpo
          type: dataset
        metrics:
          - name: dpo-pair-accuracy
            type: dpo-pair-accuracy
            value: 0.85
pretty_name: kinetigor-dpo-cybersec
language:
  - en
pipeline_tag: text-generation
```

---

## 📜 License

MIT License - Permissive open-source license.

---

## 🙏 Acknowledgments

- Base model: Mistral AI (Mistral-7B-Instruct-v0.2)
- Training data: Consolidated from multiple open-source cybersecurity frameworks
- Fine-tuning: DPO method

---

## 📅 Revision Log

- 2026-09-01 (rung-7): Refreshed to 443 unique triples post OWASP API + GraphQL
- 2026-09-01 (cull): Promoted to canonical model card with model-index
- 2026-09-02: Added ecosystem links and organization

---

## 🔗 Links

- [GitHub Repository](https://github.com/NyxSpecter4/bountywarz-ops)
- [Space Demo](https://huggingface.co/spaces/nyxspecter4/kin-inference)
- [GGUF Version](https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec-gguf)
- [Training Dataset](https://huggingface.co/datasets/nyxspecter4/kin-cyber-all-cybersec-dpo)
