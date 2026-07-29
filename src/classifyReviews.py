"""
LENS — Review Classifier (Groq / Llama 3.3 70B)  ·  BATCHED
Classifies every unique Blinkit review against the fixed 10-code context schema
and writes labeledReviews.jsonl + a theme-distribution summary.

WHAT BATCHING CHANGES (the only real difference from the per-review version)
---------------------------------------------------------------------------
The system prompt is ~620 tokens and was being re-sent on EVERY call.

    BATCH_SIZE  1 -> 1310 API calls, system prompt sent 1310x, ~1,205,000 tokens
    BATCH_SIZE  5 ->  262 API calls, system prompt sent  262x,   ~555,000 tokens
    BATCH_SIZE 10 ->  131 API calls, system prompt sent  131x,   ~474,000 tokens

So batch 5 cuts total tokens by 54% and API calls by 80%. Free tiers limit you on
BOTH requests-per-minute and tokens-per-day, so fewer+leaner calls is the single
biggest thing that stops the 429 errors.

SETUP
-----
    pip install openai pandas openpyxl python-dotenv
    # free key at https://console.groq.com -> API Keys
    # .env next to this script:
    #     GROQ_API_KEY=your_key_here

RUN
---
    python classifyReviews.py

Reads  : SanitizedBlinkitReviews.xlsx
Writes : labeledReviews.jsonl , themeSummary.csv
Resumable: re-run to continue; completed rows are skipped, failed rows retried.
"""

import os, json, time, sys, re
import pandas as pd

try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

from openai import OpenAI   # OpenAI-compatible client works with Groq

# ----- config -----
INPUT_XLSX   = os.path.join("data", "SanitizedBlinkitReviews.xlsx")
OUTPUT_JSONL = os.path.join("data", "labeledReviews.jsonl")
MODEL        = "llama-3.1-8b-instant"
client       = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
SLEEP        = 0.5

BATCH_SIZE   = 10          # reviews per API call  <-- the new setting
MAX_TOK_PER_REVIEW = 300  # output budget per review; scales with BATCH_SIZE
MAX_RETRIES  = 5

THEMES = ("habit_loop","awareness_gap","mental_model","trust_quality",
          "trust_information","price_value","ux_friction","assortment_gap",
          "delivery_ops","emotional","other")

SYSTEM = """You are a product-research analyst for Blinkit (Indian quick-commerce).
Your job: classify EACH user review below to help find barriers to users exploring NEW product categories.
Return ONLY a valid JSON object. No markdown, no prose, no code fences.

THEME definitions (choose the single best primary_theme):
- habit_loop: repeats the same basket / mission-driven, routine ordering. User orders their usual/routine products.
- awareness_gap: user states they didn't know a product or category exists on Blinkit.
- mental_model: frames Blinkit narrowly (e.g., "just for groceries", "emergency only", "only use when out of milk/bread").
- trust_quality: doubts freshness / authenticity / expiry / wrong items received / damaged packaging / short weight. Choose ONLY when product quality or authenticity is explicitly questioned. Do not choose for general delivery errors unless they directly affect product trust.
- trust_information: wants reviews/ratings/details/descriptions before buying a product (especially in new categories).
- price_value: delivery fees, packaging fees, high prices, MRP markup, "cheaper elsewhere", lack of coupons/discounts.
- ux_friction: search problems, app crash, navigation issues, discovery UI, payment or cart complications, gift card issues.
- assortment_gap: wanted a category or SKU Blinkit doesn't carry, or item is out of stock.
- delivery_ops: delivery speed, late delivery, refunds, cancellations, driver/rider behavior, customer support complaints.
- emotional: expressions of delight, ease making life better, hostel life comfort, anxiety, guilt, or impulse buying.
- other: genuine signal outside the above, general praise (e.g. "nice app", "good service") without specific details, or low-signal/emoji-only reviews.

RULES:
- evidence_span MUST be an exact substring quote (<=20 words) from THAT review. If a review is empty/emoji-only, set primary_theme="other", confidence<=0.3, evidence_span="(low-signal)".
- Never invent facts not in the text. If unsure, lower confidence.
- explores_new_category=true ONLY if the user describes trying something outside routine groceries/snacks/household.
- categories_mentioned from: grocery, snacks, household, beauty, pet, baby, personal_care, electronics, medicine, other.
- Hinglish is common; interpret it correctly.
- Return EXACTLY one result object per input review, in the same order, each with "n" = that review's number.

Output EXACTLY this shape:
{"results":[
{"n":1,"primary_theme":"selected_theme","secondary_theme":"selected_theme_or_null","sentiment":"positive|negative|neutral|mixed",
"intent":"complaint|praise|question|suggestion|story","categories_mentioned":["grocery"],
"explores_new_category":false,"barrier_to_exploration":"barrier_text_or_null","info_needed_before_trying":"info_text_or_null",
"jtbd":"jtbd_text_or_null","segment_signal":"segment_text_or_null","confidence":0.9,"evidence_span":"quote_from_review"}
]}"""

FAILED = {"primary_theme":"other","secondary_theme":None,"sentiment":"neutral",
          "intent":"story","categories_mentioned":[],"explores_new_category":False,
          "barrier_to_exploration":None,"info_needed_before_trying":None,"jtbd":None,
          "segment_signal":None,"confidence":0.0,"evidence_span":"(classification failed)"}


def classify_batch(texts):
    """Classify BATCH_SIZE reviews in one call. Returns a list aligned to texts."""
    numbered = "\n\n".join(f"[{i+1}] {t[:900]}" for i, t in enumerate(texts))
    msg = [{"role":"system","content":SYSTEM},
           {"role":"user","content":f"Classify these {len(texts)} reviews:\n\n{numbered}"}]
    raw = ""
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model=MODEL, messages=msg, temperature=0,
                max_tokens=MAX_TOK_PER_REVIEW * len(texts),
                response_format={"type":"json_object"})
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```(?:json)?|```$", "", raw).strip()
            data = json.loads(raw)
            results = data.get("results") if isinstance(data, dict) else data
            if not isinstance(results, list):
                raise ValueError("no results list")

            out = [None] * len(texts)
            for j, item in enumerate(results):
                if not isinstance(item, dict):
                    continue
                try:
                    idx = int(item.get("n", j + 1)) - 1
                except Exception:
                    idx = j
                if 0 <= idx < len(texts):
                    item.pop("n", None)
                    out[idx] = item
            return out

        except json.JSONDecodeError:
            print(f"\n    parse failed, retrying ({attempt+1}/{MAX_RETRIES})")
            time.sleep(3)
        except Exception as e:
            wait = 3
            print(f"\n    retry {attempt+1}/{MAX_RETRIES} after {wait}s ({str(e)[:70]})")
            time.sleep(wait)
    return [None] * len(texts)   # give up on this batch


def src_type(url):
    u = str(url).lower()
    if "youtube" in u or "youtu.be" in u: return "youtube"
    if "play" in u: return "playstore"
    if "app store" in u or "apps.apple" in u: return "appstore"
    if "mouthshut" in u: return "mouthshut"
    if "trustpilot" in u: return "trustpilot"
    if "reddit" in u: return "reddit"
    return "other"


def fmt_eta(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: set GROQ_API_KEY in .env"); sys.exit(1)

    df = pd.read_excel(INPUT_XLSX); df.columns = [c.strip() for c in df.columns]
    u = df.drop_duplicates("Reviews").dropna(subset=["Reviews"]).copy()
    u["Reviews"] = u["Reviews"].astype(str)
    u = u.reset_index(drop=True)
    total = len(u)

    n_calls = -(-total // BATCH_SIZE)
    print("=" * 60)
    print(f"  LENS classifier starting  ·  {MODEL}")
    print(f"  {total} unique reviews  ·  batch size {BATCH_SIZE}  ·  ~{n_calls} API calls")
    print("=" * 60)

    # resume support (failed rows are dropped so they get retried)
    done = set()
    if os.path.exists(OUTPUT_JSONL):
        keep = []
        for line in open(OUTPUT_JSONL, encoding="utf-8"):
            try:
                rec = json.loads(line)
                if rec.get("evidence_span") == "(classification failed)":
                    continue
                keep.append(line); done.add(rec["id"])
            except Exception:
                pass
        open(OUTPUT_JSONL, "w", encoding="utf-8").writelines(keep)
        if done:
            print(f"  Resuming — {len(done)}/{total} already done, "
                  f"{total-len(done)} remaining.\n")

    todo = [(f"R{i+1:04d}", r) for i, r in u.iterrows() if f"R{i+1:04d}" not in done]

    out = open(OUTPUT_JSONL, "a", encoding="utf-8")
    processed = len(done)
    newly_done = 0
    failed = 0
    start = time.time()

    try:
        for b in range(0, len(todo), BATCH_SIZE):
            chunk = todo[b:b + BATCH_SIZE]
            labels = classify_batch([r["Reviews"] for _, r in chunk])

            last_theme = "?"
            for (rid, r), label in zip(chunk, labels):
                if label is None:
                    failed += 1
                    label = dict(FAILED)
                last_theme = label.get("primary_theme", "?")
                rec = {"id": rid, "source_type": src_type(r["Source/URL"]),
                       "source_url": str(r["Source/URL"]),
                       "rating": None if pd.isna(r["Rating"]) else int(r["Rating"]),
                       **label}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                processed += 1
                newly_done += 1
            out.flush()

            # ---- live progress line (updates in place) ----
            pct = processed / total * 100
            elapsed = time.time() - start
            rate = newly_done / elapsed if elapsed > 0 else 0
            eta = fmt_eta((total - processed) / rate) if rate > 0 else "..."
            bar_len = 30
            filled = int(bar_len * processed / total)
            bar = "#" * filled + "." * (bar_len - filled)
            print(f"\r  [{bar}] {processed}/{total} ({pct:4.1f}%) "
                  f"| ETA {eta} | ok {newly_done-failed} fail {failed} | last: {last_theme:15s}",
                  end="", flush=True)

            time.sleep(SLEEP)
    except KeyboardInterrupt:
        print("\n\n  Stopped — progress saved. Re-run to resume.")
    finally:
        out.close()
        print()

    # summary
    recs = [json.loads(l) for l in open(OUTPUT_JSONL, encoding="utf-8")]
    recs.sort(key=lambda r: r.get("id", ""))          # store the file in id order
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    s = pd.Series([x.get("primary_theme", "?") for x in recs]).value_counts()
    s.to_csv(os.path.join("data", "themeSummary.csv"), index_label="primary_theme", header=["count"])

    print("\n" + "=" * 60)
    print("  ALL ROWS PROCESSED" if len(recs) >= total else "  PARTIAL — re-run to continue")
    print("=" * 60)
    print(f"  Total in file        : {total}")
    print(f"  Classified this run  : {newly_done}")
    print(f"  In output file       : {len(recs)}")
    if failed:
        print(f"  ! failed (marked)    : {failed}  (re-run to retry these)")
    print(f"  Time this run        : {fmt_eta(time.time()-start)}")
    print("-" * 60)
    print("  THEME DISTRIBUTION:")
    for theme, cnt in s.items():
        print(f"    {theme:18s} {cnt:4d}  ({cnt/len(recs)*100:.0f}%)")
    explored = sum(bool(x.get("explores_new_category")) for x in recs)
    print("-" * 60)
    print(f"  Explored a new category: {explored}/{len(recs)} ({explored/len(recs)*100:.1f}%)")
    print(f"  Files written: {OUTPUT_JSONL} , themeSummary.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()