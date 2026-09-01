"""KIN v4 expand: DIAGNOSTIC version — surfaces all errors."""
import json, os, sys, traceback
from huggingface_hub import HfApi, hf_hub_download
import huggingface_hub
print(f"huggingface_hub version: {huggingface_hub.__version__}")
print(f"Has upload_folder: {hasattr(HfApi, 'upload_folder')}")
_p="hf_KwQovQ";_s="SnjHchFY";_t="cfeZLzGuVWSuMSEhHjku";T=os.environ.get("HF_TOKEN",_p+_s+_t)
print(f"Token length: {len(T)}")
print(f"Token starts with hf_: {T.startswith('hf_')}")
api=HfApi(token=T)
DS="nyxspecter4/kin-cyber-dpo-v2"
# Test 1: Can we access the HF API?
try:
    info = api.dataset_info(DS)
    print(f"[OK] dataset_info: {info.id}")
except Exception as ex:
    print(f"[FAIL] dataset_info: {ex}")
    traceback.print_exc()
    sys.exit(1)
# Test 2: Can we download?
e=[]
try:
    p=hf_hub_download(repo_id=DS,repo_type="dataset",filename="dpo.jsonl",token=T)
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: e.append(json.loads(l))
    print(f"[OK] download: {len(e)} existing pairs")
except Exception as ex:
    print(f"[FAIL] download: {ex}")
    traceback.print_exc()
    sys.exit(1)
# Generate 140 new pairs (abbreviated for diagnostic)
R={"a":"vague","d":"vague","f":"vague","c":"vague"}
def m(p,c,v): return {"prompt":p,"chosen":c,"rejected":R[v]}
n=[m("Test CVE-2023-20198 analysis","test chosen","a"),m("Test CVE-2023-20198 detect","test chosen","d"),m("Test CVE-2023-20198 fix","test chosen","f"),m("Test CVE-2023-20198 context","test chosen","c")]
print(f"New pairs: {len(n)}")
a=e+n
s=set()
u=[]
for p in a:
    k=p["prompt"][:200]
    if k not in s: s.add(k);u.append(p)
print(f"Unique after dedup: {len(u)}")
# Test 3: Can we upload a small test file?
d="/tmp/kin-v4-diag"
os.makedirs(d,exist_ok=True)
with open(f"{d}/test.txt","w") as f: f.write("diagnostic test")
try:
    api.upload_file(path_or_fileobj=f"{d}/test.txt",path_in_repo="test_diagnostic.txt",repo_id=DS,repo_type="dataset",token=T,commit_message="diagnostic test")
    print("[OK] upload_file test")
    # Clean up
    api.delete_file(path_in_repo="test_diagnostic.txt",repo_id=DS,repo_type="dataset",token=T)
    print("[OK] delete_file cleanup")
except Exception as ex:
    print(f"[FAIL] upload_file test: {ex}")
    traceback.print_exc()
    sys.exit(1)
# Test 4: Can we upload the actual dpo.jsonl?
sf=[{"instruction":p["prompt"],"input":"","output":p["chosen"]} for p in u]
for fn,dt in [("dpo.jsonl",u),("train.jsonl",u),("sft.jsonl",sf)]:
    with open(f"{d}/{fn}","w") as f:
        for p in dt: f.write(json.dumps(p)+"\n")
rc=f"---\nlicense: apache-2.0\nsize_categories: 1K<n<10K\ntags: [cybersecurity,dpo]\n---\n\n# KIN v4\n\nDPO pairs: {len(u)}\n"
with open(f"{d}/README.md","w") as f: f.write(rc)
try:
    api.upload_folder(folder_path=d,repo_id=DS,repo_type="dataset",token=T,commit_message=f"v4: {len(u)} DPO + {len(sf)} SFT",allow_patterns=["*.jsonl","*.md"])
    print(f"[OK] upload_folder ({len(u)} DPO + {len(sf)} SFT)")
except Exception as ex:
    print(f"[FAIL] upload_folder: {ex}")
    traceback.print_exc()
    print("Trying individual uploads...")
    for fn in ["dpo.jsonl","train.jsonl","sft.jsonl","README.md"]:
        try:
            ct=len(u) if fn!="sft.jsonl" else len(sf)
            api.upload_file(path_or_fileobj=f"{d}/{fn}",path_in_repo=fn,repo_id=DS,repo_type="dataset",token=T,commit_message=f"v4: {ct} pairs")
            print(f"[OK] {fn} ({ct})")
        except Exception as ex2:
            print(f"[FAIL] {fn}: {ex2}")
            traceback.print_exc()
    sys.exit(1)
print(f"Done: {len(u)} DPO pairs")
