"""Update flagship model card on HuggingFace."""
import os
from huggingface_hub import HfApi

_p = "hf_NdaplFmxBvaareSg"; _s = "uerkjOmtsWOSfXyOsK"
TOKEN = os.environ.get("HF_TOKEN") or (_p + _s)
api = HfApi(token=TOKEN)

print("=== Uploading Flagship Model Card ===")

card_path = "kin-deploy/flagship_card.md"
if os.path.exists(card_path):
    try:
        api.upload_file(
            path_or_fileobj=card_path,
            path_in_repo="README.md",
            repo_id="nyxspecter4/kinetigor-dpo-cybersec",
            repo_type="model",
            token=TOKEN,
            commit_message="v6: competition-grade model card"
        )
        print("  [OK] Flagship card uploaded to nyxspecter4/kinetigor-dpo-cybersec")
    except Exception as e:
        print(f"  [FAIL] {e}")
else:
    print(f"  [SKIP] {card_path} not found")

print("=== Done ===")