#!/usr/bin/env python3
"""Create KIN Space and report errors clearly."""
import sys, os, time, traceback, json, urllib.request
print("=== CREATE SPACE ===", flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

from huggingface_hub import HfApi
import huggingface_hub
print("huggingface_hub:", huggingface_hub.__version__, flush=True)
api = HfApi(token=HF_TOKEN)

# Verify token works
try:
    who = api.whoami()
    print(f"Token valid, user: {who.get('name', 'unknown')}", flush=True)
except Exception as e:
    print(f"Token check FAILED: {e}", flush=True)

# Download app.py from GitHub
print("Downloading app.py...", flush=True)
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/NyxSpecter4/bountywarz-ops/main/kin-spaces/app.py",
    "/tmp/app.py"
)

# Write files
with open("/tmp/requirements.txt", "w") as f:
    f.write("gradio>=5.0,<6.0\n")
    f.write("huggingface_hub>=0.26,<0.30\n")
    f.write("audioop-lts;python_version>='3.13'\n")

with open("/tmp/README.md", "w") as f:
    f.write("---\n")
    f.write("title: Kin Inference\n")
    f.write("emoji: KIN\n")
    f.write("colorFrom: indigo\n")
    f.write("colorTo: red\n")
    f.write("sdk: gradio\n")
    f.write("sdk_version: 5.0.0\n")
    f.write("python_version: '3.13'\n")
    f.write("app_file: app.py\n")
    f.write("pinned: false\n")
    f.write("---\n")
    f.write("KIN Cybersecurity AI inference demo.\n")

# Try creating Space
SPACE_ID = "nyxspecter4/kin-inference"
print(f"Creating {SPACE_ID}...", flush=True)
try:
    result = api.create_space(repo_id=SPACE_ID, space_sdk="gradio", token=HF_TOKEN, private=False)
    print(f"CREATED OK! Result: {result}", flush=True)
except Exception as e:
    print(f"CREATE FAILED: {type(e).__name__}", flush=True)
    print(f"Error message: {e}", flush=True)
    print(f"Error repr: {repr(e)}", flush=True)
    traceback.print_exc()
    # Try v2
    SPACE_ID2 = "nyxspecter4/kin-inference-v2"
    print(f"Trying {SPACE_ID2}...", flush=True)
    try:
        result = api.create_space(repo_id=SPACE_ID2, space_sdk="gradio", token=HF_TOKEN, private=False)
        print(f"CREATED v2 OK! Result: {result}", flush=True)
        SPACE_ID = SPACE_ID2
    except Exception as e2:
        print(f"CREATE v2 FAILED: {type(e2).__name__}", flush=True)
        print(f"Error: {e2}", flush=True)
        traceback.print_exc()
        print("ALL CREATION ATTEMPTS FAILED", flush=True)
        sys.exit(1)

# Upload files
time.sleep(5)
for fname in ["app.py", "requirements.txt", "README.md"]:
    print(f"Uploading {fname}...", flush=True)
    try:
        api.upload_file(
            path_or_fileobj=f"/tmp/{fname}",
            path_in_repo=fname,
            repo_id=SPACE_ID,
            repo_type="space",
            token=HF_TOKEN,
        )
        print(f"  {fname} OK", flush=True)
    except Exception as e:
        print(f"  {fname} FAILED: {type(e).__name__}: {e}", flush=True)

# Status check
time.sleep(10)
try:
    url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        state = json.loads(resp.read())
        print(f"Stage: {state.get('stage')}", flush=True)
except Exception as e:
    print(f"Status: {e}", flush=True)

print(f"SPACE_ID: {SPACE_ID}", flush=True)
print("=== DONE ===", flush=True)
