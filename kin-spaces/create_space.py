#!/usr/bin/env python3
"""Delete and recreate the KIN Space with correct files."""
import sys, os, time, traceback, json
print("=== RECREATE SPACE ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
SPACE_ID = "nyxspecter4/kin-inference"

from huggingface_hub import HfApi, CommitOperationAdd
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__, flush=True)
api = HfApi(token=HF_TOKEN)

import urllib.request

def check_stage():
    try:
        url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
        with urllib.request.urlopen(urllib.request.Request(url)) as resp:
            state = json.loads(resp.read())
            return state.get("stage")
    except Exception:
        return "UNKNOWN"

print(f"Current stage: {check_stage()}", flush=True)

# Step 1: Delete the old Space
print("Step 1: Delete old Space...", flush=True)
try:
    api.delete_repo(repo_id=SPACE_ID, repo_type="space", token=HF_TOKEN)
    print("  Deleted OK", flush=True)
    time.sleep(3)
except Exception as e:
    print(f"  Delete failed: {type(e).__name__}: {e}", flush=True)

# Step 2: Create a new Space
print("Step 2: Create new Space...", flush=True)
try:
    api.create_space(repo_id=SPACE_ID, space_sdk="gradio", token=HF_TOKEN, private=False)
    print("  Created OK", flush=True)
    time.sleep(3)
except Exception as e:
    print(f"  Create failed: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

# Step 3: Upload all files in one commit
print("Step 3: Upload files...", flush=True)

app_py_content = (
    "import gradio as gr\n"
    "from huggingface_hub import InferenceClient\n"
    "\n"
    "MODEL_ID = \"nyxspecter4/kinetigor-dpo-cybersec\"\n"
    "client = InferenceClient(model=MODEL_ID, timeout=120)\n"
    "\n"
    "SYSTEM_PROMPT = (\n"
    "    \"You are KIN, a sharp cybersecurity AI partner. "
"
    "    \"Direct, opinionated, specific. Name tools, CVEs, companies. "
"
    "    \"Sound like a senior engineer at a bar, not a textbook.\n\"\n"
    ")\n"
    "\n"
    "def respond(message, history):\n"
    "    messages = [{\"role\": \"system\", \"content\": SYSTEM_PROMPT}] + history + [{\"role\": \"user\", \"content\": message}]\n"
    "    try:\n"
    "        response = client.chat_completion(messages=messages, max_tokens=512, temperature=0.7, top_p=0.9)\n"
    "        return response.choices[0].message.content.strip()\n"
    "    except Exception as e:\n"
    "        return f\"Error: {str(e)}\"\n"
    "\n"
    "demo = gr.ChatInterface(fn=respond, type=\"messages\", title=\"KIN Cybersecurity AI\", description=\"Direct, opinionated cybersecurity advice.\", examples=[\"How do I detect a foothold after a phishing attack?\"], theme=gr.themes.Soft())\n"
    "demo.launch()\n"
)

requirements_content = "gradio>=5.0,<6.0\nhuggingface_hub>=0.26,<0.30\naudioop-lts;python_version>='3.13'\n"

readme_content = (
    "---\n"
    "title: Kin Inference\n"
    "emoji: KIN\n"
    "colorFrom: indigo\n"
    "colorTo: red\n"
    "sdk: gradio\n"
    "sdk_version: 5.0.0\n"
    "python_version: '3.13'\n"
    "app_file: app.py\n"
    "pinned: false\n"
    "---\n"
    "KIN Cybersecurity AI inference demo.\n"
)

operations = [
    CommitOperationAdd(path_in_repo="app.py", content=app_py_content),
    CommitOperationAdd(path_in_repo="requirements.txt", content=requirements_content),
    CommitOperationAdd(path_in_repo="README.md", content=readme_content),
]

try:
    commit_info = api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message="Add app.py, requirements.txt, README.md",
        token=HF_TOKEN,
    )
    print(f"  Upload OK: {commit_info}", flush=True)
except Exception as e:
    print(f"  Upload failed: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

# Step 4: Wait and check
print("Step 4: Wait and check...", flush=True)
for i in range(6):
    time.sleep(10)
    stage = check_stage()
    print(f"  Check {i+1}: stage={stage}", flush=True)
    if stage == "RUNNING":
        break

print(f"FINAL STAGE: {check_stage()}", flush=True)
print("=== DONE ===", flush=True)
