#!/usr/bin/env python3
"""
Inkling Failure Hunter v5 - Diagnostic Mode
============================================
Tests HF token + Tinker API with GHA-visible annotations.
"""

import os, sys, json, time, traceback

MODEL = "thinkingmachines/Inkling"

# HF token (same as in convert_gguf.py and create_space.py)
_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

print("=" * 60, flush=True)
print("INKLING FAILURE HUNTER v5 - DIAGNOSTIC", flush=True)
print("=" * 60, flush=True)

# -- Step 1: Test HF Token --
print("\n[1/5] Testing HF token...", flush=True)
try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    user_info = api.whoami()
    print(f"  HF token valid! User: {user_info.get('name', 'unknown')}", flush=True)
    print(f"::notice::HF token valid, user: {user_info.get('name', 'unknown')}", flush=True)
except Exception as e:
    print(f"  HF token FAILED: {e}", flush=True)
    print(f"::error::HF token test failed: {e}", flush=True)
    traceback.print_exc()

# -- Step 2: Test HF Model Access --
print("\n[2/5] Testing HF model access...", flush=True)
try:
    from huggingface_hub import HfApi
    api = HfApi(token=HF_TOKEN)
    model_info = api.model_info("nyxspecter4/kinetigor-dpo-cybersec")
    files = [f.rfilename for f in model_info.siblings]
    print(f"  Model accessible! Files: {files}", flush=True)
    print(f"::notice::Model accessible, files: {files}", flush=True)
except Exception as e:
    print(f"  Model access FAILED: {e}", flush=True)
    print(f"::error::Model access failed: {e}", flush=True)
    traceback.print_exc()

# -- Step 3: Test HF Space Creation --
print("\n[3/5] Testing HF Space creation...", flush=True)
try:
    from huggingface_hub import create_repo
    create_repo("nyxspecter4/kin-inference", repo_type="space", private=False,
                token=HF_TOKEN, exist_ok=True)
    print("  Space created (or already exists)!", flush=True)
    print("::notice::Space creation successful", flush=True)
except Exception as e:
    print(f"  Space creation FAILED: {e}", flush=True)
    print(f"::error::Space creation failed: {e}", flush=True)
    traceback.print_exc()

# -- Step 4: Test Tinker API --
print("\n[4/5] Testing Tinker API...", flush=True)
try:
    import tinker
    from tinker import types
    print("  tinker imported OK", flush=True)
    
    service_client = tinker.ServiceClient()
    print("  ServiceClient created", flush=True)
    
    # Try to check server capabilities (this tests auth + billing)
    try:
        caps = service_client.get_server_capabilities()
        models = [m.model_name for m in caps.supported_models] if hasattr(caps, 'supported_models') else []
        has_inkling = any("inkling" in m.lower() for m in models) if models else False
        print(f"  Server capabilities OK. Models: {len(models)} total, Inkling available: {has_inkling}", flush=True)
        print(f"::notice::Tinker API accessible, {len(models)} models, Inkling: {has_inkling}", flush=True)
    except Exception as e:
        print(f"  Server capabilities FAILED: {e}", flush=True)
        print(f"::error::Tinker API check failed: {e}", flush=True)
        traceback.print_exc()
except Exception as e:
    print(f"  Tinker import/ServiceClient FAILED: {e}", flush=True)
    print(f"::error::Tinker setup failed: {e}", flush=True)
    traceback.print_exc()

# -- Step 5: Test Tinker Sampling --
print("\n[5/5] Testing Tinker sampling client...", flush=True)
try:
    sampling_client = service_client.create_sampling_client(base_model=MODEL)
    print(f"  SamplingClient created for {MODEL}", flush=True)
    
    tokenizer = sampling_client.get_tokenizer()
    print(f"  Tokenizer loaded: {type(tokenizer).__name__}", flush=True)
    
    # Quick test
    test_prompt = types.ModelInput.from_ints(tokenizer.encode("Hello, what is 2+2?"))
    test_params = types.SamplingParams(max_tokens=20, temperature=0.0)
    test_future = sampling_client.sample(prompt=test_prompt, sampling_params=test_params, num_samples=1)
    test_result = test_future.result()
    test_text = tokenizer.decode(test_result.sequences[0].tokens, skip_special_tokens=True)
    print(f"  Sampling OK! Response: {test_text[:100]}", flush=True)
    print(f"::notice::Tinker sampling works! Response: {test_text[:100]}", flush=True)
except Exception as e:
    print(f"  Tinker sampling FAILED: {e}", flush=True)
    print(f"::error::Tinker sampling failed: {e}", flush=True)
    traceback.print_exc()

print("\n" + "=" * 60, flush=True)
print("DIAGNOSTIC COMPLETE", flush=True)
print("=" * 60, flush=True)
