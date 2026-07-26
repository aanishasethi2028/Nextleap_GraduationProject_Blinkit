#!/usr/bin/env python3
"""
checkModels.py — find out which models YOUR api key can actually use.
Run this before debugging a 404 by guessing model names.

    pip install openai python-dotenv
    python3 checkModels.py
"""
import os, sys
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
from openai import OpenAI

TARGETS = [
    ("gemini", os.getenv("GEMINI_API_KEY"),
     "https://generativelanguage.googleapis.com/v1beta/openai/"),
    ("groq", os.getenv("GROQ_API_KEY"),
     "https://api.groq.com/openai/v1"),
]

for name, key, base in TARGETS:
    if not key:
        print(f"\n--- {name}: no key in .env, skipping ---")
        continue
    print(f"\n=== {name} — models available to your key ===")
    try:
        c = OpenAI(api_key=key, base_url=base)
        models = sorted(m.id for m in c.models.list())
        for m in models:
            print("   ", m)
        print(f"  ({len(models)} models)")
    except Exception as e:
        print("  ERROR listing models:", str(e)[:200])
        continue

    # try a tiny real call on the most likely candidates
    print(f"\n=== {name} — live test (does it accept JSON mode?) ===")
    cands = [m for m in models if "flash" in m or "8b" in m or "instant" in m][:6]
    for m in cands:
        for json_mode in (True, False):
            try:
                kw = {"response_format": {"type": "json_object"}} if json_mode else {}
                r = c.chat.completions.create(
                    model=m, max_tokens=20, temperature=0,
                    messages=[{"role": "user", "content": 'Reply with JSON {"ok":true}'}],
                    **kw)
                print(f"   ✅ {m}  (json_mode={json_mode})  -> {r.choices[0].message.content[:40]}")
                break
            except Exception as e:
                msg = str(e)[:90]
                print(f"   ❌ {m}  (json_mode={json_mode})  -> {msg}")