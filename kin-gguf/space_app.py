import gradio as gr
import os
import torch
from threading import Thread
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "nyxspecter4/kin-sft-lora"

print("Loading KIN model (this takes ~30s on first request)...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    token=HF_TOKEN,
    torch_dtype=torch.bfloat16,
    device_map="cpu",
    low_cpu_mem_usage=True,
)
model.eval()
print("KIN model loaded successfully!", flush=True)

SYSTEM_PROMPT = (
    "You are KIN -- a sharp cybersecurity AI partner. Direct, opinionated, specific. "
    "Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. "
    "Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. "
    "No 'As a cybersecurity AI expert.' "
    "Name products: 'CrowdStrike Falcon' not 'use EDR'. 'Duo push MFA' not 'implement MFA'."
)


def chat_response(message, history):
    if not message.strip():
        yield ""
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        max_new_tokens=600,
        temperature=0.6,
        do_sample=True,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    response = ""
    for chunk in streamer:
        response += chunk
        yield response

    thread.join()


def audit_code(code_input):
    if not code_input.strip():
        yield "Please provide a code snippet, configuration, or error trace to audit."
        return

    audit_prompt = (
        "Audit the following code/configuration for security vulnerabilities, "
        "CWEs, and contract violations:\n\n"
        + code_input
        + "\n\nProvide:\n"
        "1. Vulnerability Diagnosis (CWE and severity)\n"
        "2. Root Cause Analysis\n"
        "3. Companion Fix Patch (clean, backward-compatible code)\n"
        "4. Verification Test (how to prove the fix passes)\n"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": audit_prompt},
    ]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs,
        max_new_tokens=800,
        temperature=0.3,
        do_sample=True,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id,
        streamer=streamer,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    response = ""
    for chunk in streamer:
        response += chunk
        yield response

    thread.join()


custom_css = (
    ".gradio-container { background: #060c14 !important; color: #eaf2ff !important; "
    "font-family: Inter, system-ui, sans-serif !important; }"
    ".dark input, .dark textarea, .dark select { background: #0f1c2e !important; "
    "border-color: #12e0ff44 !important; color: #fff !important; }"
    "button.primary { background: linear-gradient(90deg, #12e0ff, #7ef0ff) !important; "
    "color: #04121a !important; font-weight: 800 !important; }"
)

with gr.Blocks(
    title="KIN -- Cybersecurity AI",
    css=custom_css,
    theme=gr.themes.Soft(primary_hue="cyan"),
) as demo:
    gr.Markdown(
        "# KIN -- Cybersecurity AI Partner\n"
        "### Empirical Security Intelligence - Zero-Hallucination Auditing - Automated Patching"
    )

    with gr.Tab("Live Security Partner"):
        gr.ChatInterface(
            fn=chat_response,
            examples=[
                "What are the top 3 moves to harden a Kubernetes cluster against lateral movement?",
                "How do I prevent SSRF when fetching user-supplied webhook URLs in Node.js?",
                "Analyze CVE-2024-3094 (xz backdoor) - what happened and what is the impact?",
                "Review my incident response plan for an ongoing ransomware breach.",
            ],
            title=None,
        )

    with gr.Tab("Code Auditor"):
        gr.Markdown(
            "Paste code or system logs for automated vulnerability detection "
            "and companion patch generation."
        )
        code_input = gr.Textbox(
            lines=10,
            label="Target Code / Error Trace",
            placeholder="Paste vulnerable function or log trace...",
        )
        audit_btn = gr.Button("Run Security Audit", variant="primary")
        audit_out = gr.Markdown()
        audit_btn.click(audit_code, inputs=code_input, outputs=audit_out)

    with gr.Tab("Model Info"):
        gr.Markdown(
            "### KIN Model Specifications\n"
            "- Base: Qwen2.5-3B-Instruct (fine-tuned via DPO)\n"
            "- Dataset: [nyxspecter4/kin-cyber-dpo-v2]"
            "(https://huggingface.co/datasets/nyxspecter4/kin-cyber-dpo-v2)\n"
            "- GGUF: [nyxspecter4/kin-sft-lora-gguf]"
            "(https://huggingface.co/nyxspecter4/kin-sft-lora-gguf)\n"
            "- Quantization: Q4_K_M (2GB) + Q8_0 (3.3GB)\n\n"
            "### Run KIN Locally with Ollama\n\n"
            "    ollama run hf.co/nyxspecter4/kin-sft-lora-gguf:Q4_K_M\n"
        )


if __name__ == "__main__":
    demo.queue().launch()
