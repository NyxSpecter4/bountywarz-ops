#!/usr/bin/env python3
"""Fix train_v5.py: syntax error + CPU compatibility patches."""
import sys

path = 'kin-gguf/train_v5.py'
with open(path, 'r') as f:
    c = f.read()

original_len = len(c)

# Fix 1: Escape unescaped quotes in NoSQL injection pair (syntax error)
# The unescaped pattern: {"user_id":123,"email":"admin@target.com","role":"user"}
# Needs to become:      {\"user_id\":123,\"email\":\"admin@target.com\",\"role\":\"user\"}
old1 = '{"user_id":123,"email":"admin@target.com","role":"user"}'
new1 = '{\\"user_id\\":123,\\"email\\":\\"admin@target.com\\",\\"role\\":\\"user\\"}'
c = c.replace(old1, new1)

# Fix 2: Remove max_prompt_length (unsupported in installed TRL version)
c = c.replace('        max_prompt_length=512,\n', '')

# Fix 3: Add max_steps for CPU to avoid timeout
c = c.replace(
    '        num_train_epochs=1,\n',
    '        num_train_epochs=1,\n        max_steps=100 if not torch.cuda.is_available() else -1,\n'
)

# Fix 4: GPU-adaptive model selection (use 0.5B on CPU, 3B on GPU)
c = c.replace(
    '    print("Loading tokenizer...")\n    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=T)',
    '    base_model = BASE_MODEL if torch.cuda.is_available() else "Qwen/Qwen2.5-0.5B-Instruct"\n'
    '    if not torch.cuda.is_available():\n'
    '        print("No GPU -- using 0.5B base for CPU-feasible training")\n'
    '    print(f"Training base: {base_model}")\n'
    '    print("Loading tokenizer...")\n'
    '    tokenizer = AutoTokenizer.from_pretrained(base_model, token=T)'
)

# Fix 4b: Use base_model in model loading + adaptive dtype
c = c.replace(
    '        BASE_MODEL,\n        torch_dtype=torch.float16,\n        device_map="auto",\n        token=T,',
    '        base_model,\n        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,\n        device_map="auto",\n        token=T,'
)

# Fix 4c: Adaptive batch size and max_length for CPU
c = c.replace(
    '        per_device_train_batch_size=2,\n        gradient_accumulation_steps=8,',
    '        per_device_train_batch_size=2 if torch.cuda.is_available() else 1,\n'
    '        gradient_accumulation_steps=8 if torch.cuda.is_available() else 2,'
)
c = c.replace(
    '        max_length=1024,',
    '        max_length=1024 if torch.cuda.is_available() else 512,'
)

# Fix 4d: Update model card to show actual base model used
c = c.replace('base_model: {BASE_MODEL}', 'base_model: {base_model}')
c = c.replace('- Base model: {BASE_MODEL}', '- Base model: {base_model}')
c = c.replace('"{BASE_MODEL}"', '"{base_model}"')

with open(path, 'w') as f:
    f.write(c)

# Verify the syntax error fix worked
if old1 in c:
    print("ERROR: Fix 1 did not apply! Unescaped quotes still present.")
    sys.exit(1)
if new1 not in c:
    print("ERROR: Fix 1 verification failed! Escaped quotes not found.")
    sys.exit(1)

print(f"All fixes applied to {path} ({original_len} -> {len(c)} bytes)")
