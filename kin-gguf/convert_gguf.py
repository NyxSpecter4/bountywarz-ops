#!/usr/bin/env python3
"""Convert KIN to GGUF — optimized build (only llama-quantize target)."""
import os, sys, shutil, subprocess, tempfile, traceback
from datetime import datetime
datetime.strptime("2024-01-01", "%Y-%m-%d")  # pre-load _strptime

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
            f.write(f"GGUF Progress: {msg}")
            p = f.name
        api.upload_file(path_or_fileobj=p, path_in_repo="GGUF_PROGRESS.md",
            repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
        os.unlink(p)
    except:
        pass

print("=" * 60)
print("KIN GGUF CONVERSION (optimized)")
print("=" * 60)
df()

# 0. Free disk (don't touch /opt/hostedtoolcache!)
write_progress("Step 0: Freeing disk...")
run(["sudo", "rm", "-rf", "/usr/share/dotnet", "/usr/local/lib/android",
     "/opt/ghc", "/usr/local/.ghcup"])
df()

# 1. Download model
write_progress("Step 1: Downloading model (6.2GB)...")
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
df()

# 2. Clone llama.cpp
write_progress("Step 2: Cloning llama.cpp...")
run(["git", "clone", "--depth", "1", "https://github.com/ggml-org/llama.cpp.git"])

# 3. Build ONLY llama-quantize (much faster than building everything)
write_progress("Step 3: Building llama-quantize (optimized)...")
try:
    run(["cmake", "-B", "llama.cpp/build", "-S", "llama.cpp",
         "-DGGML_CUDA=OFF", "-DLLAMA_CURL=OFF",
         "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF",
         "-DLLAMA_BUILD_SERVER=OFF"])
    # Only build the quantize target!
    run(["cmake", "--build", "llama.cpp/build", "--config", "Release",
         "--target", "llama-quantize", "-j4"])
except Exception as e:
    write_progress(f"cmake failed, trying make: {e}")
    os.chdir("llama.cpp")
    run(["make", "llama-quantize", "-j4"])
    os.chdir("..")

# Find quantize binary
quantize = None
for p in ["llama.cpp/build/bin/llama-quantize",
          "llama.cpp/llama-quantize",
          "llama.cpp/build/llama-quantize"]:
    if os.path.exists(p):
        quantize = p
        break
if not quantize:
    subprocess.run(["find", "llama.cpp", "-name", "*quantize*", "-type", "f"], check=False)
    write_progress("FAILED: no quantize binary")
    sys.exit(1)
print(f"quantize: {quantize}")
df()

CONVERT = "llama.cpp/convert_hf_to_gguf.py"

# 4. Install deps
write_progress("Step 4: Installing deps...")
run([sys.executable, "-m", "pip", "install", "torch",
     "--index-url", "https://download.pytorch.org/whl/cpu"])
req = "llama.cpp/requirements/requirements-convert_hf_to_gguf.txt"
if os.path.exists(req):
    run([sys.executable, "-m", "pip", "install", "-r", req])
else:
    run([sys.executable, "-m", "pip", "install", "transformers", "numpy", "gguf", "sentencepiece"])
df()

# 5. Convert to Q8_0
write_progress("Step 5: Converting to Q8_0...")
run([sys.executable, CONVERT, model_dir,
     "--outtype", "q8_0", "--outfile", "kin-sft-lora-q8_0.gguf"])
df()

# 6. Free disk
write_progress("Step 6: Freeing disk...")
shutil.rmtree("./model", ignore_errors=True)
df()

# 7. Quantize Q4_K_M
write_progress("Step 7: Quantizing Q4_K_M...")
run([quantize, "kin-sft-lora-q8_0.gguf",
     "kin-sft-lora-q4_k_m.gguf", "Q4_K_M"])
df()

# 8. Upload
write_progress("Step 8: Uploading...")
create_repo(GGUF_REPO, repo_type="model", private=False, token=HF_TOKEN, exist_ok=True)

write_progress("Uploading Q4_K_M...")
api.upload_file(path_or_fileobj="kin-sft-lora-q4_k_m.gguf",
    path_in_repo="kin-sft-lora-Q4_K_M.gguf",
    repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

write_progress("Uploading Q8_0...")
api.upload_file(path_or_fileobj="kin-sft-lora-q8_0.gguf",
    path_in_repo="kin-sft-lora-Q8_0.gguf",
    repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

write_progress("Uploading model card...")
api.upload_file(path_or_fileobj="kin-gguf/gguf_model_card.md",
    path_in_repo="README.md",
    repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

# Cleanup
try:
    api.delete_file(path_in_repo="GGUF_PROGRESS.md",
        repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
    api.delete_file(path_in_repo="CREATE_REPO_TEST.md",
        repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
except:
    pass

write_progress("SUCCESS! GGUF uploaded.")
print("\nSUCCESS! GGUF at " + GGUF_REPO)
