# 🏁 KIN HF Pro — Monday Race Playbook

> One public version upgrade to the flagship trio **every Monday**. Run this like an Indy car pit stop: every step timed, every box checked before the car leaves the bay.

## Flagship (the only public repos)
- **Model:** `nyxspecter4/kinetigor-dpo-cybersec`
- **Dataset:** `nyxspecter4/cybersec-dpo-corpus`
- **Space:** `nyxspecter4/kinetigor-dpo-cybersec-space`
- All other HF repos stay **private**.

## The 8-Stop Pit Sequence (every Monday)
1. **Expand data** — `expand-and-eval.yml`: add the week's new CVE/MITRE/OWASP pairs to the DPO corpus. Target steady growth toward 5K+ quality pairs.
2. **Train + merge** — `train-lora.yml`: DPO-train on the new corpus, then **merge into the base weights**. NEVER ship adapter-only (0 downloads).
3. **Convert GGUF** — `convert-gguf.yml`: produce Q4_K_M (primary, ~2GB) + Q8_0 (near-lossless). GGUF is the download engine.
4. **Upload to flagship** — merged safetensors + GGUF land in `kinetigor-dpo-cybersec` (not a side repo).
5. **Update model card** — `update-card.yml`: competition-grade card (see Card Spec below).
6. **Repoint + verify Space** — `kinetigor-dpo-cybersec-space` loads the flagship; confirm it builds and answers. A broken demo kills conversions.
7. **Publish dataset** — `cybersec-dpo-corpus` README + stats updated; datasets are browsed separately (free discoverability).
8. **Promote + report** — draft X thread + HF article (save to repo), then post the Slack race report to `#new-channel` with before/after numbers.

## Card Spec (match the leaders)
Minimum bar = the dealignai GLM-5.3-CYBERSECURITY / IMPERUM cards:
- YAML frontmatter: license, base_model, language, tags (cybersecurity, text-generation, gguf, dpo, en, mit), pipeline_tag, thumbnail
- **Eval table** vs base model (MMLU / a cyber benchmark) with pass/fail gate
- **Capability sections** (target 6–8): CVE analysis, detection engineering (Sigma/YARA), threat intel/ATT&CK mapping, IR, malware analysis, cloud/K8s, secure code review, GRC
- **Quickstart** for transformers + Ollama/llama.cpp + LM Studio
- **What it IS / IS NOT for** (authorized security work only)
- **BibTeX citation** (academic credibility)
- Mascot/logo image (branding drives likes — see Lily's 151 likes from 921 dl)

## Trending engine (why weekly wins)
- HF trending rewards **recency + velocity**. A Monday ship + Friday promote = two freshness spikes/week.
- GGUF quants get picked up by mradermacher/QuantFactory mirrors → multiplicative downloads.
- Every Monday push bumps `lastModified` → re-enters trending/discovery feeds.

## Competition target board (live, 1 Sep 2026)
| Model | Likes | DL |
|---|---:|---:|
| BaronLLM GGUF | 297 | 11,540 |
| GLM-5.3-CYBERSECURITY-FP8 | 29 | 227 |
| Imperum GGUF | 16 | 3,846 |
| Lily-Cybersecurity-7B | 151 | 921 |
| Qwen3.8-Flash-CYBERSECURITY | 5 | 996 |
| **KIN (flagship)** | **0** | **0** |

## Definition of done (a Monday counts only if ALL pass)
- [ ] Merged weights + GGUF live in flagship
- [ ] Competition-grade card live
- [ ] Dataset published/updated
- [ ] Space confirmed working
- [ ] Tags applied
- [ ] Promotion drafted + saved
- [ ] Slack race report posted with before/after numbers
