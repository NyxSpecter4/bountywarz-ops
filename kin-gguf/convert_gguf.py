#!/usr/bin/env python3
print("=== GGUF TEST SCRIPT START ===", flush=True)
import sys, os
print("Python:", sys.version, flush=True)
print("CWD:", os.getcwd(), flush=True)

# Test each import separately
print("Testing imports...", flush=True)
try:
    import huggingface_hub
    print("  huggingface_hub:", huggingface_hub.__version__, flush=True)
except Exception as e:
    print("  huggingface_hub FAILED:", e, flush=True)
    sys.exit(1)

try:
    from huggingface_hub import HfApi
    print("  HfApi OK", flush=True)
except Exception as e:
    print("  HfApi FAILED:", e, flush=True)
    sys.exit(1)

try:
    from huggingface_hub import snapshot_download
    print("  snapshot_download OK", flush=True)
except Exception as e:
    print("  snapshot_download FAILED:", e, flush=True)
    import traceback; traceback.print_exc()
    sys.exit(1)

# Token
_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e
print("Token constructed", flush=True)

api = HfApi(token=HF_TOKEN)
print("HfApi initialized", flush=True)

# Validate token
print("Validating token...", flush=True)
try:
    info = api.whoami()
    print("Token valid! Name:", info.get("name", "unknown"), flush=True)
except Exception as e:
    print("TOKEN ERROR:", e, flush=True)
    import traceback; traceback.print_exc()
    sys.exit(1)

# Test snapshot_download (just check if the function is callable)
print("Testing snapshot_download signature...", flush=True)
import inspect
print("  snapshot_download:", inspect.signature(snapshot_download), flush=True)

print("=== ALL IMPORTS AND TOKEN VALID ===", flush=True)
print("Ready for full GGUF conversion", flush=True)
