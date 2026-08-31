#!/usr/bin/env python3
"""Convert KIN to GGUF — v8: numpy in early install (safetensors.save_file needs it)."""
import os, sys, shutil, subprocess, tempfile, traceback, json
from datetime import datetime
datetime.strptime("2024-01-01", "%Y-%m-%d")

HF_TOKEN = "hf_KwQovQ" + "SnjHchFY" + "cfeZLzGuVWSuMSEhHjku"

MODEL_ID = "nyxspecter4/kin-sft-lora"
GGUF_REPO = "nyxspecter4/kin-sft-lora-gguf"

from huggingface_hub import HfApi, snapshot_download, create_repo
api = HfApi(token=HF_TOKEN)

def write_progress(msg):
    print(f"[PROGRESS] {msg}", flush=True)
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(f"# GGUF Conversion Progress\n\n{msg}\n")
            p = f.name
        api.upload_file(path_or_fileobj=p, path_in_repo="GGUF_PROGRESS.md",
            repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
        os.unlink(p)
    except Exception as e:
        print(f"[WARN] Failed to write progress: {e}", flush=True)

def run(cmd, **kw):
    print(f">>> {' '.join(cmd) if isinstance(cmd, list) else cmd}", flush=True)
    return subprocess.run(cmd, check=True, **kw)

def run_capture(cmd):
    print(f">>> {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout[-2000:], flush=True)
    if r.stderr:
        print(r.stderr[-2000:], flush=True)
    return r.returncode, r.stdout, r.stderr

def df():
    subprocess.run(["df", "-h", "/"], check=False)

try:
    print("=" * 60)
    print("KIN GGUF CONVERSION v8 (numpy + torch + safetensors early)")
    print("=" * 60)
    df()

    # 0. Free disk
    write_progress("Step 0: Freeing disk...")
    run(["sudo", "rm", "-rf", "/usr/share/dotnet", "/usr/local/lib/android",
         "/opt/ghc", "/usr/local/.ghcup", "/usr/local/share/boost",
         "/usr/local/share/rust", "/opt/az"])
    df()

    # 0b. Install ALL deps needed for patching (torch, numpy, safetensors)
    write_progress("Step 0b: Installing torch + numpy + safetensors (early)...")
    run([sys.executable, "-m", "pip", "install", "numpy"])
    run([sys.executable, "-m", "pip", "install", "torch",
         "--index-url", "https://download.pytorch.org/whl/cpu"])
    run([sys.executable, "-m", "pip", "install", "safetensors"])
    # Verify all three import
    rc, out, err = run_capture([sys.executable, "-c",
        "import torch, numpy, safetensors; print('torch', torch.__version__); print('numpy', numpy.__version__); print('safetensors OK')"])
    if rc != 0:
        write_progress(f"FAILED: early import check failed:\n{err}")
        sys.exit(1)
    df()

    # 1. Download model (exclude adapter files!)
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
    print(f"Model dir: {model_dir}")
    for f in sorted(os.listdir(model_dir)):
        fp = os.path.join(model_dir, f)
        sz = os.path.getsize(fp) if os.path.isfile(fp) else "DIR"
        print(f"  {f} ({sz})")
    df()

    # 1b. Check for .base_layer. in safetensors index and patch if needed
    write_progress("Step 1b: Checking tensor names for PEFT artifacts...")
    index_path = os.path.join(model_dir, "model.safetensors.index.json")
    needs_patch = False
    if os.path.exists(index_path):
        with open(index_path) as f:
            idx = json.load(f)
        wm = idx.get("weight_map", {})
        base_layer_keys = [k for k in wm if ".base_layer." in k]
        lora_keys = [k for k in wm if ".lora_A." in k or ".lora_B." in k or "lora_embedding" in k]
        if base_layer_keys:
            print(f"Found {len(base_layer_keys)} tensors with .base_layer. prefix")
            print(f"Found {len(lora_keys)} LoRA adapter tensors")
            needs_patch = True
            new_wm = {}
            for k, v in wm.items():
                if ".lora_A." in k or ".lora_B." in k or "lora_embedding" in k:
                    continue
                new_k = k.replace(".base_layer.", ".")
                new_wm[new_k] = v
            idx["weight_map"] = new_wm
            with open(index_path, "w") as f:
                json.dump(idx, f)
            print(f"Patched index: {len(wm)} -> {len(new_wm)} tensors")

    if needs_patch:
        write_progress("Step 1c: Patching safetensors files to remove .base_layer. ...")
        from safetensors.torch import load_file, save_file

        shard_files = sorted([f for f in os.listdir(model_dir) if f.endswith(".safetensors")])
        for shard in shard_files:
            shard_path = os.path.join(model_dir, shard)
            print(f"  Loading {shard}...")
            tensors = load_file(shard_path)
            print(f"  Loaded {len(tensors)} tensors")
            keys_to_rename = [k for k in list(tensors.keys()) if ".base_layer." in k]
            for k in keys_to_rename:
                new_k = k.replace(".base_layer.", ".")
                tensors[new_k] = tensors.pop(k)
            lora_keys = [k for k in list(tensors.keys()) if ".lora_A." in k or ".lora_B." in k or "lora_embedding" in k]
            for k in lora_keys:
                del tensors[k]
            print(f"  Renamed {len(keys_to_rename)} tensors, removed {len(lora_keys)} LoRA tensors")
            save_file(tensors, shard_path, metadata={"format": "pt"})
            del tensors
            print(f"  Saved {shard}")
        write_progress("Step 1c: Safetensors patched successfully")
    else:
        print("No .base_layer. artifacts found — no patching needed")
    df()

    # 2. Clone llama.cpp
    write_progress("Step 2: Cloning llama.cpp...")
    if os.path.exists("llama.cpp"):
        shutil.rmtree("llama.cpp")
    run(["git", "clone", "--depth", "1", "https://github.com/ggml-org/llama.cpp.git"])
    df()

    # 3. Build ONLY llama-quantize
    write_progress("Step 3: Building llama-quantize (optimized)...")
    run(["cmake", "-B", "llama.cpp/build", "-S", "llama.cpp",
         "-DGGML_CUDA=OFF", "-DLLAMA_CURL=OFF",
         "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF",
         "-DLLAMA_BUILD_SERVER=OFF"])
    run(["cmake", "--build", "llama.cpp/build", "--config", "Release",
         "--target", "llama-quantize", "-j4"])

    quantize = None
    for p in ["llama.cpp/build/bin/llama-quantize",
              "llama.cpp/llama-quantize",
              "llama.cpp/build/llama-quantize"]:
        if os.path.exists(p):
            quantize = p
            break
    if not quantize:
        subprocess.run(["find", "llama.cpp", "-name", "*quantize*", "-type", "f"], check=False)
        write_progress("FAILED: no quantize binary found")
        sys.exit(1)
    print(f"quantize: {quantize}")
    df()

    CONVERT = "llama.cpp/convert_hf_to_gguf.py"
    if not os.path.exists(CONVERT):
        for alt in ["llama.cpp/convert_hf_to_gguf.py",
                     "llama.cpp/scripts/convert_hf_to_gguf.py"]:
            if os.path.exists(alt):
                CONVERT = alt
                break
        else:
            write_progress(f"FAILED: convert script not found")
            sys.exit(1)
    print(f"convert script: {CONVERT}")

    # 4. Install remaining deps (torch already installed)
    write_progress("Step 4: Installing remaining deps...")
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    req = "llama.cpp/requirements/requirements-convert_hf_to_gguf.txt"
    if os.path.exists(req):
        run([sys.executable, "-m", "pip", "install", "-r", req])
    else:
        run([sys.executable, "-m", "pip", "install", "transformers", "numpy", "gguf", "sentencepiece"])
    run([sys.executable, "-m", "pip", "install", "accelerate"])

    for pkg in ["gguf", "transformers", "torch", "numpy"]:
        rc, out, err = run_capture([sys.executable, "-c",
            f"import {pkg}; print('{pkg}', getattr({pkg}, '__version__', 'OK'))"])
        if rc != 0:
            write_progress(f"FAILED: cannot import {pkg}:\n{err}")
            sys.exit(1)
    df()

    # 5. Convert to F16
    write_progress("Step 5a: Converting to F16 GGUF...")
    rc, out, err = run_capture([sys.executable, CONVERT, model_dir,
         "--outtype", "f16", "--outfile", "kin-f16.gguf"])
    if rc != 0:
        write_progress(f"FAILED at step 5a (convert F16):\nSTDOUT:\n{out[-3000:]}\nSTDERR:\n{err[-3000:]}")
        sys.exit(1)
    df()

    # 5b. Free model dir
    write_progress("Step 5b: Freeing model dir...")
    shutil.rmtree("./model", ignore_errors=True)
    df()

    # 6. Quantize Q8_0 from F16
    write_progress("Step 6: Quantizing Q8_0...")
    rc, out, err = run_capture([quantize, "kin-f16.gguf",
         "kin-sft-lora-q8_0.gguf", "Q8_0"])
    if rc != 0:
        write_progress(f"FAILED at step 6 (quantize Q8_0):\nSTDOUT:\n{out[-3000:]}\nSTDERR:\n{err[-3000:]}")
        sys.exit(1)
    df()

    # 7. Quantize Q4_K_M from F16
    write_progress("Step 7: Quantizing Q4_K_M...")
    rc, out, err = run_capture([quantize, "kin-f16.gguf",
         "kin-sft-lora-q4_k_m.gguf", "Q4_K_M"])
    if rc != 0:
        write_progress(f"FAILED at step 7 (quantize Q4_K_M):\nSTDOUT:\n{out[-3000:]}\nSTDERR:\n{err[-3000:]}")
        sys.exit(1)
    df()

    # 7b. Free F16
    write_progress("Step 7b: Freeing F16...")
    os.unlink("kin-f16.gguf")
    df()

    # 8. Upload
    write_progress("Step 8: Uploading to HF...")
    create_repo(GGUF_REPO, repo_type="model", private=False, token=HF_TOKEN, exist_ok=True)

    write_progress("Uploading Q4_K_M...")
    api.upload_file(path_or_fileobj="kin-sft-lora-q4_k_m.gguf",
        path_in_repo="kin-sft-lora-Q4_K_M.gguf",
        repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

    write_progress("Uploading Q8_0...")
    api.upload_file(path_or_fileobj="kin-sft-lora-q8_0.gguf",
        path_in_repo="kin-sft-lora-Q8_0.gguf",
        repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

    card_path = "kin-gguf/gguf_model_card.md"
    if os.path.exists(card_path):
        write_progress("Uploading model card...")
        api.upload_file(path_or_fileobj=card_path,
            path_in_repo="README.md",
            repo_id=GGUF_REPO, repo_type="model", token=HF_TOKEN)

    try:
        api.delete_file(path_in_repo="GGUF_PROGRESS.md",
            repo_id=MODEL_ID, repo_type="model", token=HF_TOKEN)
    except:
        pass

    write_progress("SUCCESS! GGUF uploaded to " + GGUF_REPO)
    print("\nSUCCESS! GGUF at " + GGUF_REPO)

except Exception as e:
    tb = traceback.format_exc()
    print(tb, flush=True)
    write_progress(f"EXCEPTION:\n{tb[-4000:]}")
    sys.exit(1)
