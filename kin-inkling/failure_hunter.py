#!/usr/bin/env python3
"""
Inkling Cybersecurity Failure Case Hunter v3
=============================================
Tests Thinking Machines' Inkling model via the Tinker API across 25
cybersecurity tasks. Collects failure cases for $250 Tinker credit submission.

FIXES from v2:
  - create_sampling_client(base_model=...) NOT model_name=
  - SamplingParams(max_tokens=, temperature=) â no 'effort' field
  - Prompt via types.ModelInput.from_ints(tokenizer.encode(text))
  - Sync sample().result() with result.samples[0].tokens
  - Tokenizer loaded with HF token for gated model access
"""

import os, sys, json, time, traceback

# ââ Tinker API key ââââââââââââââââââââââââââââââââââââââââââââââââââ
_t¬ÄôÑµ°µ)åQ)}Ñ¬Èôa-Ýd)}Ñ¬Ìô­aLÑÕUh)}Ñ¬Ðôié4ÌÙÐ)}Ñ¬ÔôÙÁiÉM\)}Ñ¬Øô½¨Í9)e)}Ñ¬Üôi½Aµ5¼)}Ñ¬àôÕÍ=ÕÙ,)}Ñ¬äôÝÕaá()Q%9-I}-dô½Ì¹¹Ù¥É½¸¹Ð Q%9-I}A%}-d¤½È¡}Ñ¬Ä¬}Ñ¬È¬}Ñ¬Ì¬}Ñ¬Ð¬}Ñ¬Ô¬}Ñ¬Ø¬}Ñ¬Ü¬}Ñ¬à¬}Ñ¬ä¤()}¡Äô¡}-ÝE½ÙD)}¡ÈôM¹©J!¡d)}¡Ìôi1éÔ)}¡ÐôY]MÕ5M )}¡Ôô!)­Ô)!}Q=-8ô½Ì¹¹Ù¥É½¸¹Ð !}Q=-8¤½È¡}¡Ä¬}¡È¬}¡Ì¬}¡Ð¬}¡Ô¤)5=0ôÑ¡¥¹­¥¹µ¡¥¹Ì½%¹­±¥¹