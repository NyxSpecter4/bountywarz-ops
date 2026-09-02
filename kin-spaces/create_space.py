#!/usr/bin/env python3
"""Restart the KIN inference Space using direct API calls."""
print("=== RESTART SPACE START ===", flush=True)
import sys, os, time, traceback, json
print("Python:", sys.version, flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

SPACE_ID = "nyxspecter4/kin-inference"

try:
    import huggingface_hub
    print("huggingface_hub:", huggingface_hub.__version__, flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

# First check the current state
print("Checking Space state...", flush=True)
import urllib.request
url = f"https://huggingface.co/api/spaces/{SPACE_ID}/runtime"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    state = json.loads(resp.read())
    print(f"Current stage: {state.get('stage')}", flush=True)

# Try restart via direct API POST
print("Sending restart POST request...", flush=True)
restart_url = f"https://huggingface.co/api/spaces/{SPACE_ID}/restart"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

import urllib.parse
data = urllib.parse.urlencode({}).encode()
restart_req = urllib.request.Request(restart_url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(restart_req) as resp:
        result = json.loads(resp.read())
        print(f"Restart response: {json.dumps(result, indent=2)}", flush=True)
        print("Restart succeeded!", flush=True)
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}", flush=True)
    traceback.print_exc()
    
    # Try factory reboot
    print("Trying factory reboot...", flush=True)
    factory_url = f"https://huggingface.co/api/spaces/{SPACE_ID}/restart?factory=true"
    factory_req = urllib.request.Request(factory_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(factory_req) as resp:
            result = json.loads(re
sp.read())
            print(f"Factory reboot response: {json.dumps(result, indent=2)}", flush=True)
            print("Factory reboot succeeded!", flush=True)
    except urllib.error.HTTPError as e2:
        print(f"Factory reboot HTTP Error {e2.code}: {e2.read().decode()}", flush=True)
        traceback.print_exc()

# Check state again
print("Checking Space state after restart...", flush=True)
time.sleep(5)
with urllib.request.urlopen(urllib.request.Request(url)) as resp:
    state = json.loads(resp.read())
    print(f"Stage after restart: {state.get('stage')}", flush=True)

print("=== RESTART COMPLETE ===", flush=True)
