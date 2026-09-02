import gradio as gr
from huggingface_hub import InferenceClient

MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"
client = InferenceClient(model=MODEL_ID, timeout=120)

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
        response = client.chat_completion(
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
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
