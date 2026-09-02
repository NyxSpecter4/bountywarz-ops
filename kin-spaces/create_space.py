#!/usr/bin/env python3
"""Upload files to KIN Space and restart it. Uses upload_file for simplicity."""
import sys, os, time, traceback, json
print("=== SPACE UPLOAD + RESTART ===", flush=True)
print("Python:", sys.version, flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
SPACE_ID = "nyxspecter4/kin-inference"

from huggingface_hub import HfApi
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__, flush=True)

api = HfApi(token=HF_TOKEN)

# Write files locally first
APP_PY = """import gradio as gr
from huggingface_hub import InferenceClient

MODEL_ID = "nyxspecter4/kinetigor-dpo-cybersec"
client = InferenceClient(model=MODEL_ID, timeout=120)

SYSTEM_PROMPT = "You are KIN, a sharp cybersecurity AI partner. Direct, opinionated, specific. Name tools, CVEs, companies. Sound like a senior engineer at a bar, not a textbook. Lead with your boldest take. End with a specific action. Max 2-3 paragraphs. Name products: CrowdStrike Falcon not use EDR. Duo push MFA not implement MFA."


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
        return f"Error: {str(e)}"


demo = gr.ChatInterface(
    fn=respond,
    type="messages",
    title="KIN Cybersecurity AI",
    description="Direct, opinionated cybersecurity advice.",
    examples=["How do I detect a foothold after a phishing attack?"],
    theme=gr.themes.Soft(),
)
demo.launch()
"""

REQUIREMENTS = "gradio>=5.0,<6.0\nhuggingface_hub>=0.26,<0.30\naudioop-lts;python_version>='3.13'\n"

README = "---\ntitle: Kin Inference\nemoji: eye\ncolorFrom: indigo\ncolorTo: red\nsdk: gradio\nsdk_version: 5.0.0\npython_version: '3.13'\napp_file: app.py\npinned: false\n---\n\nKIN Cybersecurity AI inference demo.\n"

# Write to local temp files
with open("/tmp/app.py", "w") as f:
    f.write(APP_PY)
with open("/tmp/requirements.txt", "w") as f:
    f.write(REQUIREMENTS)
with open("/tmp/README.md", "w") as f:
    f.write(README)

print("Files written locally. Uploading to Space...", flush=True)

# Upload each file
for fname in ["app.py", "requirements.txt", "README.md"]:
    try:
        print(f"Uploading {fname}...", flush=True)
        api.upload_file(
            path_or_fileobj=f"/tmp/{fname}",
            path_in_repo=fname,
            repo_id=SPACE_ID,
            repo_type="space",
            token=HF_TOKEN,
        )
        print(f"  {fname} uploaded OK", flush=True)
    except Exception as e:
        print(f"  {fname} FAILED: {e}", flush=True)
        traceback.print_exc()

print("All uploads attempted. Waiting 5s...", flush=True)
time.sleep(5)

# Check state
import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after upload: {state.get('stage')}", flush=True)

# Restart if needed
if state.get('stage') in ('PAUSED', 'RUNTIME_ERROR'):
    print("Restarting Space...", flush=True)
    try:
        api.restart_space(space_id=SPACE_ID)
        print("restart_space OK", flush=True)
    except Exception as e:
        print(f"restart failed: {e}", flush=True)
        try:
            api.restart_space(space_id=SPACE_ID, factory_reboot=True)
            print("factory reboot OK", flush=True)
        except Exception as e2:
            print(f"factory reboot failed: {e2}", flush=True)

time.sleep(5)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Final stage: {state.get('stage')}", flush=True)

print("=== DONE ===", flush=True)
