# Graduation Project — Master Solution
## Blinkit | Growth Team | Increasing New-Category Adoption Among Monthly Active Customers

**Chosen product:** Blinkit (largest catalog breadth: groceries → beauty, electronics, pet, baby, stationery — maximum room for cross-category adoption)

**Business goal (restated as a metric):**
> **Category Adoption Rate (CAR)** = % of Monthly Active Customers who purchase from ≥1 category they have never bought from (or haven't bought from in 90 days) in a given month.

---

# PART 1 — AI-Powered Discovery Engine ("LENS")

## 1.1 What it is
LENS (Listening ENgine for Shoppers) is a repeatable pipeline that ingests unstructured user voice (Play Store, App Store, Reddit, X, YouTube comments, Quora) and converts it into structured, evidence-linked insights about *why users don't explore new categories*.

## 1.2 Architecture

```
┌─────────────── DATA SOURCES ───────────────┐
│ Play Store · App Store · Reddit (r/india,  │
│ r/bangalore, r/delhi, r/IndianFood) ·      │
│ X/Twitter · Quora · YouTube comments       │
└──────────────────┬─────────────────────────┘
                   ▼
        [1] SCRAPING LAYER (n8n + Apify)
                   ▼
        [2] CLEANING & DEDUP (Python node)
                   ▼
        [3] LANGUAGE DETECT + TRANSLATE
            (Hinglish → English, GPT-4o-mini)
                   ▼
        [4] LLM CLASSIFICATION (Claude Sonnet)
            → theme, sentiment, intent, barrier,
              segment signal, JTBD, confidence
                   ▼
        [5] EMBEDDINGS (text-embedding-3-small)
                   ▼
        [6] VECTOR DB (Supabase pgvector)
                   ▼
        [7] CLUSTERING (HDBSCAN on embeddings)
                   ▼
        [8] INSIGHT SYNTHESIS (Claude, per cluster)
                   ▼
        [9] VALIDATION LAYER (human spot-check +
            confidence scoring + triangulation)
                   ▼
        [10] DASHBOARD (Streamlit on HF Spaces)
```

## 1.3 Stack choice & tradeoffs

| Layer | Chosen | Why | Alternatives considered |
|---|---|---|---|
| Orchestration | **n8n (cloud free tier)** | Visual, evaluator can inspect the workflow via shared link; native HTTP/webhook nodes; scheduled runs | Zapier (expensive per-task, weak loops), LangGraph (code-heavy, harder to demo), CrewAI (agent overkill for a linear pipeline) |
| Scraping | **Apify actors** (`google-play-scraper`, `app-store-scraper`, Reddit scraper) + Reddit JSON API | Managed, legal-ToS-aware, free tier covers ~5k reviews | Custom Playwright (fragile), SerpAPI (search only) |
| Classification LLM | **Claude Sonnet** | Best at nuanced Hinglish sentiment + strict JSON output | GPT-4o (comparable; cost similar), Gemini Flash (cheaper, weaker on JSON discipline) |
| Embeddings | OpenAI `text-embedding-3-small` | Cheap ($0.02/1M tokens), good for clustering | Voyage, Cohere |
| Vector DB | **Supabase pgvector** | Free, SQL-queryable, doubles as the app DB for Part 4 | Pinecone (free tier limits), Qdrant (self-host overhead), Weaviate |
| Dashboard | **Streamlit → Hugging Face Spaces** | Free public URL = your "link to test the workflow" deliverable | Retool (paid), Notion (static) |

**Why not "just ask Perplexity"?** Perplexity summarizes; it doesn't produce traceable, quantified, per-review classifications. The assignment rewards a *system*, not a search.

## 1.4 Core prompts (copy-paste ready)

### Prompt A — Per-review classifier (run for each review/comment)
```
SYSTEM:
You are a product research analyst for a quick-commerce platform.
Classify the user feedback below. Respond with ONLY valid JSON, no markdown.

Schema:
{
 "relevant_to_category_exploration": true|false,
 "theme": one of ["habit_loop","price_trust","quality_trust","awareness_gap",
   "mission_mindset","ux_friction","assortment_gap","delivery_trust",
   "discount_dependence","other"],
 "sentiment": "positive"|"negative"|"neutral"|"mixed",
 "intent": "complaint"|"praise"|"question"|"suggestion"|"story",
 "categories_mentioned": [strings],
 "barrier_to_new_category": string or null,   // verbatim-grounded, 1 line
 "jtbd": string or null,                       // "When I ..., I want ..., so I can ..."
 "segment_signal": string or null,             // e.g. "young professional", "parent", "pet owner"
 "confidence": 0.0-1.0,
 "verbatim_evidence": string                   // exact quote fragment, ≤20 words
}

USER:
Source: {{source}}
Text: {{review_text}}
```

### Prompt B — Cluster synthesizer (run per HDBSCAN cluster)
```
You are a Principal UX Researcher. Below are {{n}} classified feedback items
from one semantic cluster. Produce ONE insight card as JSON:

{
 "insight_title": string,            // states the finding, not the topic
 "so_what_for_growth": string,       // implication for new-category adoption
 "frequency": {{n}},
 "representative_quotes": [3 quotes with source URLs],
 "affected_segments": [strings],
 "confidence": "high"|"medium"|"low",// high = ≥15 items + ≥2 source types
 "counter_evidence": string or null, // items in cluster contradicting the insight
 "validation_needed": string         // what primary research must confirm
}
Rules: never invent quotes; if evidence is thin, say confidence low.
```

### Prompt C — Insight validator (adversarial pass)
```
You are a skeptical PM hiring manager. For the insight below, answer:
1. Is the claim actually supported by the quotes, or is it over-generalized?
2. Could sampling bias explain it? (app reviews over-index on complaints)
3. What is the simplest alternative explanation?
Output: {"verdict":"keep"|"revise"|"discard", "reason": string}
```

## 1.5 Validation strategy (this is what evaluators look for)
1. **Human spot-check:** manually label 50 random reviews yourself; compare to LLM labels; report agreement % (target ≥85%). Show the confusion table in the appendix.
2. **Source triangulation:** an insight only reaches "high confidence" if it appears in ≥2 independent source types (e.g., Play Store + Reddit).
3. **Adversarial pass:** Prompt C run on every insight; discarded insights listed in appendix (shows intellectual honesty — huge scoring signal).
4. **Known failure cases to document:** sarcasm in Hinglish, delivery-partner complaints polluting "trust" theme, review bombing after price changes, duplicate reviews across app versions.

## 1.6 Sample output (illustrative format — regenerate with your real run)
```json
{
 "insight_title": "Users mentally file Blinkit as a 'top-up grocery app', so non-grocery categories are invisible even when browsed past daily",
 "so_what_for_growth": "Awareness isn't the constraint — mental model is. Merchandising alone won't fix it; the moment of need must be intercepted.",
 "confidence": "medium",
 "validation_needed": "Confirm in interviews: do users know Blinkit sells e.g. pet food / stationery? Can they name 3 non-grocery categories unprompted?"
}
```

## 1.7 Hypotheses from secondary research (to be tested — these are the LENS starting priors)
Grounded in public reports (URLs for your appendix):
- Quick commerce is habitual and mission-driven: it's ~5–6% of urban household grocery spend and used for "top-up" missions — USDA FAS India report: https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=India's+E-commerce+and+Quick+Commerce+Market_Mumbai_India_IN2025-0043
- Impulse buying and loyalty-program engagement shape behavior (Bangalore survey study, n=128): https://research-archive.org/index.php/rars/preprint/view/3704
- Category expansion beyond grocery is the industry's stated growth lever: Bain "How India Shops Online 2025": https://www.bain.com/insights/how-india-shops-online-2025/ ; IBEF sectoral analysis: https://www.ibef.org/research/case-study/the-evolution-of-quick-commerce-in-india-a-sectoral-analysis
- Pricing/discount perception study across cities: Kearney: https://www.kearney.com/documents/291362523/308218538/The+rise+of+quick+commerce-transforming+Indias+retail+consumer+behaviors+and+employment+dynamics-PDF.pdf

**Hypothesized barriers (H1–H5), each falsifiable in interviews:**
- **H1 Mission mindset:** users open Blinkit with a fixed shopping "mission" (milk/veggies/refill); anything outside the mission is cognitively invisible.
- **H2 Reorder loop:** "Buy again" / past-order UI actively reinforces repetition — the product itself trains the habit.
- **H3 Trust asymmetry:** users trust Blinkit for standardized packaged goods but not for judgment-heavy categories (beauty efficacy, pet food suitability, baby safety) where they rely on Amazon reviews / friends / doctors.
- **H4 Price anchoring:** users assume quick commerce = convenience premium, so "considered" purchases feel irrational to make here.
- **H5 Awareness gap:** users genuinely don't know the breadth of catalog (electronics, stationery, puja items).

---

# PART 2 — Primary Research (you must run this for real — 5–6 calls, ~20 min each)

## 2.1 Segment choice: **Young working professionals & working couples, 24–35, metro cities, ordering ≥4×/month**
Why: highest MAC share, highest disposable income, already habituated (so the *habit* problem is purest here), and most reachable for you to recruit (colleagues, alumni, LinkedIn, society WhatsApp groups).

## 2.2 Research objective
Understand why habituated quick-commerce users repeat the same 2–3 categories, and what conditions would make them try a new category — to validate/refute H1–H5.

## 2.3 Screener (Google Form — create it, link it in the deck)
1. Age band, city, occupation
2. Which quick-commerce apps used in last 30 days?
3. Orders per month (screen in ≥4)
4. Which categories bought in last 3 months? (checklist)
5. Willing for a 20-min call? (contact)

## 2.4 Consent statement (read at start)
"This is an academic research interview. I'll record notes (audio only if you allow). Your name will be anonymized; responses used only for a student project. You can skip any question or stop anytime. Okay to proceed?"

## 2.5 Interview script (semi-structured, 20–25 min)

**Warm-up (2 min)**
1. Walk me through the last time you opened Blinkit. What did you order?

**Habit & mental model (5 min)**
2. When do you typically open the app — what triggers it?
3. If I say "Blinkit", what kind of shop is it in your head? (listen for mission mindset — H1)
4. Show me how you usually order. (screen-share/observe — do they use "Buy again"? — H2)

**Discovery (4 min)**
5. Have you ever bought something on Blinkit you'd never bought there before? Tell me that story. (critical incident)
6. How did you find it — search, browsing, banner, someone told you?
7. Name 3 things you'd be surprised Blinkit sells. Then: did you know it sells [pet food / stationery / skincare]? (H5)

**Trust & information (5 min)**
8. Imagine buying [face serum / pet food / baby wipes] today. Where would you buy it and why not Blinkit? (H3)
9. What would you want to know before buying that on Blinkit?
10. Do you check reviews on Blinkit? Where do you check instead?

**Pricing (3 min)**
11. Do you think Blinkit is cheaper, same, or costlier than Amazon/DMart for non-grocery? Have you ever compared? (H4)

**Category switching (3 min)**
12. What was the last new *type* of thing you started buying online anywhere? What convinced you?
13. If Blinkit wanted you to try one new category next month, what would it have to do?

**Close (1 min)**
14. Magic wand: change one thing about how you shop on these apps.

## 2.6 Analysis kit
- **Notes template:** columns = Question | Verbatim | Observation | Hypothesis touched (H1–H5) | Surprise?
- **Affinity mapping:** dump every verbatim on stickies (FigJam free), cluster bottom-up, name clusters *after* clustering, not before.
- **Coding framework:** code each quote to {barrier type, trigger, workaround, segment signal}; count frequency across participants (n/6).
- **Contradiction log:** explicitly record where interviews *disagree* with LENS output — this is your Part 3 gold ("primary research validated X but challenged Y").
- **Insight bar:** an insight needs ≥3/6 participants + at least one LENS cluster to count as validated.

> ⚠️ Do NOT fabricate these interviews. Six 20-minute calls over two evenings is enough, and real quotes are visibly different from generated ones. Recruit via office Slack, alumni groups, apartment WhatsApp.

---

# PART 3 — Problem Definition (template — fill numbers/quotes from your actual research)

## 3.1 Problem statement (draft to refine)
> Habituated Blinkit users (24–35, metro, 4+ orders/month) open the app with a fixed replenishment mission and complete it via the reorder loop in under 90 seconds. Judgment-heavy categories (beauty, pet, baby) never enter consideration because the app offers no trust-building information at the moment of decision — so users default to Amazon/specialty apps for those, capping Blinkit's share of wallet.

## 3.2 JTBD (primary)
- Functional: "When I'm running low on daily items, I want to restock in seconds, so my routine isn't interrupted." (served — and it *causes* the problem)
- Unserved: "When I need something outside my routine, I want enough confidence to buy it without research, so I don't have to open three other apps."

## 3.3 Root cause — 5 Whys
1. Why don't users buy new categories? → They don't consider Blinkit for them.
2. Why? → Mental model: Blinkit = grocery top-up shop.
3. Why? → Every session reinforces the same loop (search/buy-again → checkout).
4. Why? → The app optimizes for speed of *repeat* purchase; discovery costs time.
5. Why? → No mechanism converts an adjacent life-need signal (has a pet, has a baby, buys gym snacks) into a low-friction, trust-backed first purchase.
**Root cause:** the product's core strength (speed via habit) structurally suppresses discovery; discovery must therefore ride *on top of* the habit loop, not fight it.

## 3.4 Existing workarounds (validate in interviews)
Amazon for reviewed/considered purchases; specialty apps (Nykaa, supertails, FirstCry); offline chemist/kirana; asking friends/WhatsApp groups.

## 3.5 Why it matters
- **User value:** one app for more of life's needs; less research overhead; faster resolution of non-routine needs.
- **Business value:** cross-category buyers → higher AOV, higher retention, higher LTV; category expansion is the industry's stated growth lever (Bain 2025). Even +2pp CAR on Blinkit's MAC base is a large incremental GMV pool (size it with public MTU numbers in your deck; mark as estimate).

## 3.6 Metrics
- **North Star:** Category Adoption Rate (CAR) — % MAC with ≥1 new-category purchase/month.
- **Input metrics:** new-category consideration rate (PDP views outside historical categories), first-purchase conversion, starter-pack CTR.
- **Guardrails:** checkout time p50 (habit must not slow), order frequency, 30-day retention, refund/return rate in new categories (trust proxy), contribution margin.

## 3.7 Prioritization (RICE — fill with your numbers)
Compare 3 candidate solutions: (a) AI discovery copilot, (b) cross-category bundles/starter packs, (c) post-checkout "one new thing" nudge. Score Reach/Impact/Confidence/Effort; the MVP below is (a)+(b) hybrid because it attacks the root cause (trust at moment of decision) rather than just awareness.

---

# PART 4 — AI-Native MVP: **"Blinkit Scout"** — a category-discovery copilot

## 4.1 Concept
A chat + card interface that:
1. Takes the user's typical basket (simulated from 3 quick questions or pasted order history),
2. Detects adjacent life-context signals ("buys dog treats? → pet care"; "buys protein bars? → fitness/personal care"),
3. Recommends ONE new category per week as a **Starter Pack**: 3 top SKUs + *why-you-can-trust-this* info (price vs MRP benchmark, best-rated pick, usage tip) — answering exactly the information gap H3 surfaced,
4. Rides on the habit loop: surfaces at *post-checkout* ("your order's on the way — 1 thing people like you added this week"), never before checkout (guardrail: checkout speed).

## 4.2 Architecture & stack
```
Next.js (frontend, Vercel) 
  → /api/scout (serverless route)
     → Claude API (recommendation + trust-info generation, strict JSON)
     → Supabase (catalog sample table + user session state + pgvector
       reuse from Part 1 → real review snippets as trust evidence!)
```
The elegant move: **LENS's vector DB feeds Scout** — real user quotes about products become the trust layer. Part 1 and Part 4 are literally the same system. Say this on a slide; it's your differentiator.

## 4.3 System prompt (core of Scout)
```
You are Scout, Blinkit's category discovery assistant.
Input: user's last 10 purchased items + categories never purchased.
Task: recommend exactly ONE new category and a 3-item starter pack.
Rules:
- The category must be adjacent to an observed life signal; state the signal.
- Never recommend a category the user already buys.
- For each item: one-line "why", price band, and one real review snippet
  (provided in context) — never invent reviews.
- Tone: like a smart flatmate, not a salesman. ≤80 words total.
- Output strict JSON: {category, signal, items:[{name, why, price_band,
  review_snippet}], one_liner_pitch}
- If no strong signal exists, output {category: null} — do not force it.
```

## 4.4 Evaluation
- **Eval dataset:** 25 synthetic user baskets (5 personas × 5 variants).
- **Test cases:** signal present → correct adjacent category; no signal → null; already-bought category → never recommended; empty basket → onboarding questions.
- **Edge cases:** vegetarian basket → never recommend meat; baby items present → safety-toned copy; budget basket → no premium SKUs.
- **Metric for demo:** relevance rated by 5 friends blind (target ≥4/5 "would consider").

## 4.5 Deployment (15 minutes, free)
1. `npx create-next-app scout` → add one API route + one page.
2. Push to GitHub → import to **Vercel** → add `ANTHROPIC_API_KEY` env var.
3. Supabase free project → one `catalog` table (seed 60 SKUs across 8 categories from Blinkit's public listings) + one `reviews` table (seed from your LENS run).
4. Public URL = your production link deliverable.

---

# THE 10-SLIDE DECK (insight-based titles, per guidelines)

1. **"Blinkit won the habit — and the habit is now the ceiling"** (context + goal metric CAR)
2. **"We built LENS: 4,000+ public user voices, classified and validated"** (the required 1-slider: architecture diagram + test link)
3. **"What the data says: users file Blinkit as a top-up grocery shop"** (top 3 LENS insights, confidence levels, quotes)
4. **"6 real interviews confirmed the trust gap — and killed one of our hypotheses"** (validation matrix H1–H5: validated / challenged / rejected)
5. **"The problem: our speed loop structurally suppresses discovery"** (problem statement + 5 Whys + workaround map)
6. **"The opportunity: +Xpp CAR = ₹Y Cr incremental GMV"** (sizing, marked assumptions)
7. **"Solution principle: discovery must ride the habit, not fight it"** (3 options + RICE, why Scout wins)
8. **"Meet Scout: trust-backed starter packs at the post-checkout moment"** (product walkthrough + live link)
9. **"Scout runs on LENS: real user voice becomes the trust layer"** (architecture, eval results)
10. **"How we'll know it worked"** (metrics tree: North Star, inputs, guardrails, experiment design: 2-week A/B, post-checkout module vs control)

**Compliance checklist:** no name anywhere in deck · ≤10 slides · min font 14 (Slides/PPT) · color-blind-safe palette (avoid red/green pairing; use blue/orange) · all links set to "anyone with link can view" · file name format `<YourInitials> Blinkit` · export PDF <40MB.

---

# EXECUTION PLAN (deadline Aug 4 — you have ~2 weeks)

| Days | Task |
|---|---|
| 1–3 | Build LENS in n8n; run on 3–5k reviews; spot-check 50 |
| 3–5 | Recruit + schedule 6 interviews (screener form out on day 1!) |
| 5–9 | Run interviews; affinity map; validation matrix |
| 9–11 | Build + deploy Scout on Vercel; run evals |
| 11–13 | Deck + PDF + appendix; self-critique pass (Prompt C on your own deck) |
| 14 | Buffer + submission |

# WHAT TO ASK CLAUDE FOR NEXT (I can generate each of these fully)
1. The complete n8n workflow JSON for LENS (importable)
2. The full Next.js + Claude API code for Scout, ready for Vercel
3. The Streamlit dashboard code for the LENS insights
4. The Google Form questions + observation sheet + affinity template
5. The actual 10-slide deck (PPTX) once your real research data is in
