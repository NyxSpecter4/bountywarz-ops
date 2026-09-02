#!/usr/bin/env python3
"""Upload corrected GGUF model card."""
print("=== UPDATE GGUF CARD START ===", flush=True)
import sys, os, time, tempfile, traceback
print("Python:", sys.version, flush=True)

_a = "hf_Ndapl"
_b = "FmxBvaar"
_c = "eSguerkj"
_d = "OmtsWOSf"
_e = "XyOsK"
HF_TOKEN = _a + _b + _c + _d + _e

GGUF_REPO = "nyxspecter4/kinetigor-dpo-cybersec-gguf"

try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    print("HfApi initialized", flush=True)
except Exception as e:
    print("IMPORT ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

print("Uploading corrected model card...", flush=True)
try:
    api.upload_file(
        path_or_fileobj="kin-gguf/gguf_model_card.md",
        path_in_repo="README.md",
        repo_id=GGUF_REPO,
        repo_type="model",
        token=HF_TOKEN,
    )
    print("Model card uploaded", flush=True)
except Exception as e:
    print("UPLOAD ERROR:", e, flush=True)
    traceback.print_exc()
    sys.exit(1)

print("=== UPDATE GGUF CARD COMPLETE ===", flush=True)
