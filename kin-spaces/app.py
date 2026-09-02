import os
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"

print("Loading tokenizer...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
print("Loading model (Qwen2.5-0.5B DPO)...", flush=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
model.eval()
print("Model loaded on", model.device, flush=True)

SYSTEM_PROMPT = (
    "You are KIN — a sharp cybersecurity AI partner. Direct, opinionated, specific. "
    "Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. "
    "Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. "
    "Open with your take, not your title. No 'As a cybersecurity AI expert.' "
    "Name products: 'CrowdStrike Falcon' not 'use EDR'. 'Duo push MFA' not 'implement MFA'."
)


def respond(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": message}]
    try:
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            out = model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
            )
        reply = tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        return reply.strip()
    except Exception as e:
        return f"[KIN hit an error — try again.] Error: {str(e)}"


demo = gr.ChatInterface(
    fn=respond,
    type="messages",
    title="KIN — Cybersecurity AI",
    description="Direct, opinionated cybersecurity advice. Like a senior engineer at a bar, not a textbook.",
    examples=[
        "How do I detect a foothold after a phishing attack?",
        "What went wrong with the MGM hack?",
        "Explain CVE-2024-3094 in plain English.",
        "What EDR should I actually buy?",
    ],
    theme=gr.themes.Soft(),
)

demo.launch()
