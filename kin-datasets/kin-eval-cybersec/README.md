# KIN Cybersecurity Evaluation Dataset

Public evaluation dataset for testing and benchmarking the KIN model.

## Dataset Structure

Evaluation prompts and expected responses for cybersecurity tasks.

## Usage

With Transformers:

from datasets import load_dataset

dataset = load_dataset("nyxspecter4/kin-eval-cybersec")

## Dataset Splits

| Split | Description | Size |
|-------|-------------|------|
| test | Public evaluation prompts | 100 examples |
| validation | Internal validation | 50 examples |

## Model Compatibility

Designed for: nyxspecter4/kinetigor-dpo-cybersec

## Related Resources

- Model: https://huggingface.co/nyxspecter4/kinetigor-dpo-cybersec
- Space: https://huggingface.co/spaces/nyxspecter4/kin-inference
- Training Data: https://huggingface.co/datasets/nyxspecter4/kin-cyber-all-cybersec-dpo

## License

Apache 2.0

## Tags

cybersecurity, evaluation, text-generation, mitre-attack, owasp, nist-csf
license:apache-2.0, language:en, task:text-generation, region:us
