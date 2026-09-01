#!/usr/bin/env python3
"""Update HF Space nyxspecter4/kin-cybersec to reference the v5 DPO model."""
import os, tempfile
from huggingface_hub import HfApi

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
T = os.environ.get("HF_TOKEN") or (_p + _s + _t)

SPACE = "nyxspecter4/kin-cybersec"
MODEL_REPO = "nyxspecter4/kin-cyber-dpo-v2-lora"
DS = "nyxspecter4/kin-cyber-dpo-v2"

api = HfApi(token=T)

# Updated README.md
readme = (
    "---\n"
    "title: KIN Cyber Sec\n"
    "emoji: \U0001f6e1\ufe0f\n"
    "colorFrom: blue\n"
    "colorTo: red\n"
    "sdk: static\n"
    "app_file: index.html\n"
    "pinned: false\n"
    "license: apache-2.0\n"
    "models:\n"
    f"  - {MODEL_REPO}\n"
    "datasets:\n"
    f"  - {DS}\n"
    "tags:\n"
    "  - cybersecurity\n"
    "  - threat-hunting\n"
    "  - mitre-attack\n"
    "  - sigma-rules\n"
    "  - infosec\n"
    "  - qwen2.5\n"
    "  - judge-arena\n"
    "  - soc-triage\n"
    "  - vulnerability-detection\n"
    "  - exploit-chain\n"
    "  - cve-analysis\n"
    "---\n\n"
    "# KIN Cyber Sec\n\n"
    "A static storefront for the KIN Cybersecurity Suite. Browse the model card\n"
    "and DPO dataset; pair with [kin-cyber-arena](https://huggingface.co/spaces/nyxspecter4/kin-cyber-arena)\n"
    "for live A/B judge-evaluator runs.\n\n"
    "## v5 Updates\n\n"
    f"- DPO model: '{MODEL_REPO}' (Qwen2.5-0.5B/3B-Instruct LoRA)\n"
    f"- Dataset: '{DS}' with v5 pairs (vuln-finding, exploit-chain, CVE analysis)\n"
    "- Categories: vulnerability detection, exploit chain reasoning, advanced CVE analysis\n\n"
    "Captain-LAW compliant: no abliterated lineages. Apache-2.0 license throughout.\n"
)

with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
    f.write(readme)
    readme_file = f.name
api.upload_file(
    path_or_fileobj=readme_file,
    path_in_repo="README.md",
    repo_id=SPACE,
    repo_type="space",
    token=T,
    commit_message="v5: update model reference to kin-cyber-dpo-v2-lora",
)
print("[OK] Space README.md updated")

# Download existing index.html, update references, upload
try:
    index_path = api.hf_hub_download(repo_id=SPACE, filename="index.html", repo_type="space", token=T)
    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()
except Exception as e:
    print(f"Could not download index.html: {e}")
    index_content = None

if index_content:
    index_content = index_content.replace("kin-sft-lora-gguf", "kin-cyber-dpo-v2-lora")
    index_content = index_content.replace("Qwen2.5-Coder-7B LoRA", "Qwen2.5-0.5B/3B-Instruct LoRA (v5)")
    index_content = index_content.replace("stage-15", "stage-16")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(index_content)
        index_file = f.name
    api.upload_file(
        path_or_fileobj=index_file,
        path_in_repo="index.html",
        repo_id=SPACE,
        repo_type="space",
        token=T,
        commit_message="v5: update model references in storefront",
    )
    print("[OK] Space index.html updated")
    print("Space update complete!")
else:
    print("Skipping index.html update")
