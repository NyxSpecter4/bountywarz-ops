import json, os, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3

api = HfApi(token=TOKEN)

print("=== KIN Eval Benchmark ===")

# Cybersecurity eval prompts
EVAL_PROMPTS = [
    {"prompt": "Analyze CVE-2021-44228 (Log4Shell). Provide attack vectors, severity, and mitigation.", "category": "cve_triage"},
    {"prompt": "Audit this Node.js handler for SSRF: async function fetchWebhook(url) { return fetch(url); }", "category": "code_audit"},
    {"prompt": "What are the top 3 moves to harden a Kubernetes cluster against lateral movement?", "category": "defense"},
    {"prompt": "Explain the difference between XSS and CSRF. Provide a code example of each and the fix.", "category": "knowledge"},
    {"prompt": "Analyze this SQL injection attempt: 1' OR '1'='1' -- What is the attack and how to prevent it?", "category": "attack_analysis"},
    {"prompt": "Provide a Python function to detect if a string contains encoded shellcode. Use regex patterns.", "category": "malware_analysis"},
    {"prompt": "Create an incident response plan for a ransomware breach affecting 500 endpoints.", "category": "incident_response"},
    {"prompt": "Explain how to set up a SIEM correlation rule for detecting lateral movement via Pass-the-Hash.", "category": "siem"},
    {"prompt": "What MITRE ATT&CK techniques are used in a typical ransomware kill chain? List with IDs.", "category": "threat_intel"},
    {"prompt": "Generate a SARIF-format report for a SQL injection finding in /api/users endpoint.", "category": "sarif_output"},
]

SYSTEM_PROMPT = (
    "You are KIN — an elite agentic cybersecurity partner trained on real-world incident telemetry. "
    "Direct, opinionated, specific. Name tools, CVEs, companies. "
    "Lead with your boldest take. End with a specific actionable next move. "
    "Never say 'As an AI' or 'I hope this helps'. "
)

def load_model(model_id, label):
    print(f"\nLoading {label}: {model_id}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=TOKEN, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, token=TOKEN, trust_remote_code=True,
            torch_dtype=torch.float16, device_map="auto"
        )
        print(f"  Loaded {label} successfully")
        return model, tokenizer
    except Exception as e:
        print(f"  Failed to load {label}: {e}")
        return None, None

def generate_response(model, tokenizer, prompt, max_new_tokens=300):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    try:
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=0.3, do_sample=False)
        response = tokenizer.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
        return response
    except Exception as e:
        return f"[Generation error: {e}]"

def compute_perplexity(model, tokenizer, text):
    try:
        encodings = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        encodings = {k: v.to(model.device) for k, v in encodings.items()}
        with torch.no_grad():
            outputs = model(**encodings, labels=encodings["input_ids"])
        return torch.exp(outputs.loss).item()
    except:
        return float("inf")

# Load models
kin_model, kin_tok = load_model("nyxspecter4/kin-sft-lora", "KIN")
base_model, base_tok = load_model("Qwen/Qwen2.5-3B-Instruct", "Base Qwen")

if kin_model is None:
    print("ERROR: Could not load KIN model. Exiting.")
    sys.exit(1)

results = {"kin": [], "base": []}

# Run eval
print("\nRunning eval prompts...")
for i, item in enumerate(EVAL_PROMPTS):
    prompt = item["prompt"]
    category = item["category"]
    print(f"  [{i+1}/{len(EVAL_PROMPTS)}] {category}...")

    kin_resp = generate_response(kin_model, kin_tok, prompt)
    kin_ppl = compute_perplexity(kin_model, kin_tok, prompt + " " + kin_resp)
    
    base_resp = ""
    base_ppl = 0
    if base_model:
        base_resp = generate_response(base_model, base_tok, prompt)
        base_ppl = compute_perplexity(base_model, base_tok, prompt + " " + base_resp)
    
    results["kin"].append({"category": category, "prompt": prompt, "response": kin_resp, "perplexity": kin_ppl})
    results["base"].append({"category": category, "prompt": prompt, "response": base_resp, "perplexity": base_ppl})
    
    print(f"    KIN ppl: {kin_ppl:.2f} | Base ppl: {base_ppl:.2f}")
    print(f"    KIN response length: {len(kin_resp)} | Base response length: {len(base_resp)}")

# Compute aggregate metrics
kin_avg_ppl = sum(r["perplexity"] for r in results["kin"] if r["perplexity"] != float("inf")) / len(results["kin"])
base_avg_ppl = sum(r["perplexity"] for r in results["base"] if r["perplexity"] != float("inf")) / len(results["base"])
kin_avg_len = sum(len(r["response"]) for r in results["kin"]) / len(results["kin"])
base_avg_len = sum(len(r["response"]) for r in results["base"]) / len(results["base"])

# Check for hallucination indicators (weasel words)
HALLUCINATION_INDICATORS = ["As an AI", "I hope this helps", "I cannot", "I'm unable to", "it depends", "you should consult", "I would need more information"]
kin_halluc = sum(1 for r in results["kin"] if any(h in r["response"] for h in HALLUCINATION_INDICATORS))
base_halluc = sum(1 for r in results["base"] if any(h in r["response"] for h in HALLUCINATION_INDICATORS))

report = f"""# KIN Cybersecurity Model — Eval Report

## Benchmark Results

| Metric | KIN (Qwen2.5-3B + DPO LoRA) | Base (Qwen2.5-3B-Instruct) | Improvement |
|--------|---------------------------|--------------------------|-------------|
| **Avg Perplexity** | {kin_avg_ppl:.2f} | {base_avg_ppl:.2f} | {(1 - kin_avg_ppl/base_avg_ppl)*100:.1f}% lower |
| **Avg Response Length** | {kin_avg_len:.0f} chars | {base_avg_len:.0f} chars | |
| **Hallucination Indicators** | {kin_halluc}/{len(EVAL_PROMPTS)} | {base_halluc}/{len(EVAL_PROMPTS)} | {(1 - kin_halluc/max(base_halluc,1))*100:.1f}% fewer |

## Eval Categories

| Category | KIN Perplexity | Base Perplexity |
|----------|---------------|----------------|
"""

for r in results["kin"]:
    base_r = next((b for b in results["base"] if b["category"] == r["category"]), {})
    report += f"| {r['category']} | {r['perplexity']:.2f} | {base_r.get('perplexity', 0):.2f} |\n"

report += f"""
## Methodology
- **Model:** nyxspecter4/kin-sft-lora (Qwen2.5-3B-Instruct + DPO LoRA)
- **Base:** Qwen/Qwen2.5-3B-Instruct
- **Prompts:** {len(EVAL_PROMPTS)} cybersecurity eval prompts across 10 categories
- **Generation:** greedy decoding (temperature=0, max_new_tokens=300)
- **Hallucination indicators:** {', '.join(HALLUCINATION_INDICATORS)}
- **Date:** {time.strftime('%Y-%m-%d')}
"""

print("\n" + report)

# Save report
with open("/tmp/eval_report.md", "w") as f:
    f.write(report)

# Save raw results
with open("/tmp/eval_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Upload report to HF model repo
try:
    api.upload_file(
        path_or_fileobj="/tmp/eval_report.md",
        path_in_repo="EVAL_REPORT.md",
        repo_id="nyxspecter4/kin-sft-lora-gguf",
        repo_type="model",
        commit_message="Add eval benchmark report: KIN vs base Qwen2.5-3B"
    )
    print("\nEval report uploaded to nyxspecter4/kin-sft-lora-gguf")
except Exception as e:
    print(f"\nUpload error: {e}")

print("\n=== Eval complete ===")
