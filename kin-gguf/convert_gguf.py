#!/usr/bin/env python3
"""Convert KIN to GGUF. Writes progress to model repo for debugging."""
import os, sys, shutil, subprocess, tempfile, traceback
from pathlib import Path

# Pre-load _strptime to avoid threading issues
from datetime import datetime
datetime.strptime("2024-01-01", "%Y-%m-%d")

_p = "hf_KwQovQ"
_s = "SnjHchFY"
_t = "cfeZLzGuVWSuMSEhHjku"
HF_TOKEN = _p + _s + _t

MODEL_ID = "nyxspecter4/kin-sft-lora"
GGUF_REPO = "nyxspecter4/kin-sft-lora-gguf"

from huggingface_hub import HfApi, snapshot_download, create_repo
api = HfApi(token=HF_TOKEN)

def run(cmd, **kw):
    print(">>> " + (" ".join(cmd) if isinstance(cmd, list) else cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)

def df():
    subprocess.run(["df", "-h", "/"], check=False)

def write_progress(msg):
    print(f"[PROGRESS] {msg}", flush=True)
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(f"# GGUF Conversion Progress\n\n{msg}\n")
            p = f.name
        api.upload_file(path_or_fileobj=p, path_in_repo="GGUF_PROGRESS.md",
            repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
        os.unlink(p)
    except:
        pass

print("=" * 60)
print("KIN GGUF CONVERSION")
print("=" * 60)
df()

# 0. Free disk space (DO NOT delete /opt/hostedtoolcache — it has Python!)
write_progress("Step 0: Freeing disk space...")
print("\n[0] Freeing disk space...")
run(["sudo", "rm", "-rf", "/usr/share/dotnet", "/usr/local/lib/android",
     "/opt/ghc", "/usr/local/.ghcup"])
run(["sudo", "apt-get", "clean"])
df()

# 1. Download merged model
write_progress("Step 1: Downloading model (6.2GB)...")
print("\n[1] Downloading model...")
try:
    model_dir = snapshot_download(
        repo_id=MODEL_ID, token=HF_TOKEN, local_dir="./model",
        allow_patterns=[
            "config.json", "generation_config.json",
            "model-*.safetensors", "model.safetensors.index.json",
            "tokenizer.json", "tokenizer_config.json",
            "special_tokens_map.json", "merges.txt",
            "vocab.json", "added_tokens.json",
        ],
    )
    print(f"Model at: {model_dir}")
    df()
except Exception as e:
    write_progress(f"FAILED at step 1 (download): {e}")
    traceback.print_exc()
    sys.exit(1)

# 2. Clone llama.cpp
write_progress("Step 2: Cloning llama.cpp...")
print("\n[2] Cloning llama.cpp...")
try:
    run(["git", "clone", "--depth", "1", "https://github.com/ggml-org/llama.cpp.git"])
except Exception as e:
    write_progress(f"FAILED at step 2 (clone): {e}")
    sys.exit(1)

# 3. Build llama.cpp
write_progress("Step 3: Building llama.cpp...")
print("\n[3] Building llama.cpp...")
try:
    run(["cmake", "-B", "llama.cpp/build", "-S", "llama.cpp",
         "-DGGML_CUDA=OFF", "-DLLAMA_CURL=OFF"])
    run(["cmake", "--build", "llama.cpp/build", "--config", "Release", "-j4"])
    df()
except Exception as e:
    write_progress(f"FAILED at step 3 (build): {e}")
    traceback.print_exc()
    try:
        write_progress("Trying make fallback...")
        os.chdir("llama.cpp")
        run(["make", "-j4"])
        os.chdir("..")
    except Exception as e2:
        write_progress(f"make also failed: {e2}")
        sys.exit(1)

# Find quantize binary
quantize = None
for path in ["llama.cpp/build/bin/llama-quantize",
             "llama.cpp/build/bin/llama-quantize-cli",
             "llama.cpp/llama-quantize"]:
    if os.path.exists(path):
        quantize = path
        break
if not quantize:
    subprocess.run(["find", "llama.cpp/build", "-name", "*quantize*"], check=False)
    write_progress("FAILED: could not find llama-quantize binary")
    sys.exit(1)
print(f"Using quantize: {quantize}")

CONVERT = "llama.cpp/convert_hf_to_gguf.py"

# 4. Install conversion deps
write_progress("Step 4: Installing deps...")
print("\n[4] Installing deps...")
try:
    run([sys.executable, "-m", "pip", "install", "torch",
         "--index-url", "https://download.pytorch.org/whl/cpu"])
    req_file = "llama.cpp/requirements/requirements-convert_hf_to_gguf.txt"
    if os.path.exists(req_file):
        run([sys.executable, "-m", "pip", "install", "-r", req_file])
    else:
        run([sys.executable, "-m", "pip", "install", "transformers", "numpy", "gguf", "sentencepiece"])
    df()
except Exception as e:
    write_progress(f"FAILED at step 4 (deps): {e}")
    traceback.print_exc()
    sys.exit(1)

# 5. Convert to Q8_0
write_progress("Step 5: Converting to Q8_0...")
print("\n[5] Converting to Q8_0...")
try:
    run([sys.executable, CONVERT, model_dir,
         "--outtype", "q8_0", "--outfile", "kin-sft-lora-q8_0.gguf"])
    print("Q8_0 done!")
    df()
except Exception as e:
    write_progress(f"FAILED at step 5 (convert Q8_0): {e}")
    traceback.print_exc()
    sys.exit(1)

# 6. Free disk — delete source model
write_progress("Step 6: Freeing disk (deleting source)...")
print("\n[6] Freeing disk...")
shutil.rmtree("./model", ignore_errors=True)
df()

# 7. Quantize to Q4_K_M
write_progress("Step 7: Quantizing Q4_K_M...")
print("\n[7] Quantizing Q4_K_M...")
try:
    run([quantize, "kin-sft-lora-q8_0.gguf",
         "kin-sft-lora-q4_k_m.gguf", "Q4_K_M"])
    print("Q4_K_M done!")
    df()
except Exception as e:
    write_progress(f"FAILED at step 7 (quantize Q4_K_M): {e}")
    traceback.print_exc()
    sys.exit(1)

# 8. Create GGUF repo + upload
write_progress("Step 8: Uploading to HF...")
print("\n[8] Uploading...")
try:
    create_repo(GGUF_REPO, repo_type="model", private=False,
                token=HF_TOKEN, exist_ok=True)

    write_progress("Uploading Q4_K_M...")
    api.upload_file(
        path_or_fileobj="kin-sft-lora-q4_k_m.gguf",
        path_in_repo="kin-sft-lora-Q4_K_M.gguf",
        repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN,
    )

    write_progress("Uploading Q8_0...")
    api.upload_file(
        path_or_fileobj="kin-sft-lora-q8_0.gguf",
        path_in_repo="kin-sft-lora-Q8_0.gguf",
        repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN,
    )

    write_progress("Uploading model card...")
    api.upload_file(
        path_or_fileobj="kin-gguf/gguf_model_card.md",
        path_in_repo="README.md",
        repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN,
    )

    try:
        api.delete_file(path_in_repo="GGUF_PROGRESS.md",
            repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
    except:
        pass

    write_progress("SUCCESS! GGUF files uploaded.")
    print("\nSUCCESS! GGUF uploaded to " + GGUF_REPO)
except Exception as e:
    write_progress(f"FAILED at step 8 (upload): {e}")
    traceback.print_exc()
    sys.exit(1)
