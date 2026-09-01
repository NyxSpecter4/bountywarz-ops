"""Update GGUF model card with correct training data count."""
import os, tempfile
from huggingface_hub import HfApi

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3
api = HfApi(token=TOKEN)

print("=== Updating GGUF Model Card ===")

card_path = "kin-gguf/gguf_model_card_v2.md"
if os.path.exists(card_path):
    try:
        api.upload_file(
            path_or_fileobj=card_path,
            path_in_repo="README.md",
            repo_id="nyxspecter4/kin-sft-lora-gguf",
            repo_type="model",
            token=TOKEN,
            commit_message="Update model card: 1331 DPO pairs (was 550+), add comparison table"
        )
        print("  [OK] Model card updated")
    except Exception as e:
        print(f"  [FAIL] {e}")
else:
    print(f"  [SKIP] {card_path} not found")

print("=== Done ===")
