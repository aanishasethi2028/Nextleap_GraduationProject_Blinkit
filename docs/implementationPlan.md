# Implementation Plan: LENS (Listening ENgine for Shoppers)

Phase-wise implementation plan for the LENS category-discovery insight engine. Phases follow [docs/architecture.md](./architecture.md) and [docs/context.md](./context.md).
---

## Roadmap Overview

```
PART 1 TRACK (this document)              PART 2 TRACK (runs in parallel)
┌────────────────────────────────┐        ┌────────────────────────────────┐
│ P1: Ingestion & Sanitization   │ ✅     │ Recruit 6 interviewees         │ ← START TODAY
└────────────────────────────────┘        │ (survey respondents = warm list)│
              │                            └────────────────────────────────┘
              ▼                                          │
┌────────────────────────────────┐                       ▼
│ P2: LLM Classification         │ 🔄     ┌────────────────────────────────┐
└────────────────────────────────┘        │ Run + transcribe interviews    │
              │                            └────────────────────────────────┘
              ▼                                          │
┌────────────────────────────────┐                       │
│ P3: Semantic Clustering        │ 🔲                    │
└────────────────────────────────┘                       │
              │                                          │
              ▼                                          │
┌────────────────────────────────┐                       │
│ P4: Insight Synthesis & Ranking│ 🔲                    │
└────────────────────────────────┘                       │
              │                                          │
              ▼                                          ▼
┌────────────────────────────────────────────────────────────────┐
│ P5: Validation & Audit  ◄── triangulates reviews + survey +     │ 🔲 CRITICAL
│                             interviews                          │
└────────────────────────────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────┐
│ P6: Streamlit Dashboard        │ 🔲 (graded public link)
└────────────────────────────────┘
              │
              ▼
┌────────────────────────────────┐
│ P7: Findings Report + 1-slider │ 🔲 (graded deliverables)
└────────────────────────────────┘
```

---

## Phase-Wise Execution Details

### Phase 1: Ingestion & Text Sanitization
* **Objectives**: Collect supplementary quick-commerce comments to counter app-store complaint bias; merge and deduplicate; flag low-signal rows; establish stable IDs.
* **Component code & output**:
  * `collectData.py` — YouTube Data API v3 (**277 comments yielded**) and Reddit public `.json` endpoints (**1 comment yielded**; Quora **0**). Output: `social_data.xlsx`.
  * `sanitizeReviews.py` — cleans raw input, drops exact duplicate review text (**17 removed**), flags rows with **fewer than 10 latin/devanagari letters** (**55 flagged**, retained), assigns stable IDs `R0001…R1310`, writes `SanitizedBlinkitReviews.xlsx`.
  * `sanitize_report.txt` — automated report of counts, source frequencies, rating distribution. **This artifact is the evidence behind every corpus number cited elsewhere.**
* **Corpus checklist**: 1,327 ingested → **1,310 unique**; 55 low-signal retained; 1,255 usable rich reviews.

---

### Phase 2: LLM Classification Pipeline
* **Objectives**: Classify all 1,310 reviews against the taxonomy (**10 substantive codes + `other`**).
* **Component code & output**:
  * `classifyReviews.py` — Groq API via the OpenAI SDK wrapper, **`llama-3.1-8b-instant`**.
    *Model note:* originally specified `llama-3.3-70b-versatile`; switched after sustained HTTP 429 rate limits. The 8B model is adequate for bounded classification but weaker on nuanced Hinglish and borderline theme calls — **this raises the importance of Phase 5, and the model name must be reported alongside the agreement score.**
  * **Hinglish**: interpreted in-prompt; no separate translation stage.
  * **Resumability**: reads existing IDs from `labeledReviews.jsonl` and skips them.
  * **Rate-limit guardrails**: `SLEEP = 4s` throttle plus exponential backoff on 429; rate-limit errors are retried, not recorded as failures.
  * **Outputs**: `labeledReviews.jsonl`, `themeSummary.csv`.

---

### Phase 3: Semantic Clustering
* **Status**: 🔲 **PLANNED**
* **Objectives**: Embed classified reviews and surface micro-themes through unsupervised clustering.
* **Implementation**:
  1. Create `src/clustering.py`.
  2. Embed with a local sentence-transformer (`all-MiniLM-L6-v2`) — runs offline, no API cost.
  3. Apply HDBSCAN; noisy/unmatched reviews are excluded automatically.
  4. **Cluster–label convergence check** against LLM primary themes to expose fuzzy boundaries.
* **⚠ Risk & fallback**: HDBSCAN on ~1,310 short texts frequently assigns a large share to noise (`label = -1`). **If more than ~40% lands in noise, or fewer than 6 usable clusters emerge, fall back to theme-based grouping** (group by `primary_theme`, sub-split large themes by sentiment/segment) and report the fallback honestly. Clustering is a means to insight, not a deliverable in itself — do not burn days tuning it.
* **Outputs**: `src/clustering.py`; cluster assignments mapped to review IDs.

---

### Phase 4: Insight Synthesis & Ranking
* **Status**: 🔲 **PLANNED**
* **Objectives**: Turn clusters into prioritized insight cards ranked by strategic value, not complaint volume.
* **Implementation**:
  1. Create `src/synthesis.py`.
  2. Per cluster, feed representative reviews **with source URLs** to a higher-nuance model to draft the finding, the "so-what" for category adoption, affected segments, and counter-evidence.
  3. Compute **Opportunity = Frequency × Severity × Addressability × Strategic Fit**.
  4. **Quarantine `delivery_ops`** so operational complaints don't crowd out growth barriers.
  5. Tag every card with the research question(s) it answers (Q1–Q8). **Any of Q1–Q8 the corpus cannot answer is recorded as a gap and routed to Part 2 — never answered by inference.**
* **Outputs**: `src/synthesis.py`; `data/insights.json`.

---

### Phase 5: Verification & Validation Layer
* **Status**: 🔲 **PLANNED** — **highest-scoring component; protect this time**
* **Objectives**: Establish that the insights are true, not artifacts of method.
* **Implementation**:
  1. Create `src/validate.py` plus the audit sheet.
  2. **Human-agreement audit** — hand-label **50 reviews** and compute LLM–human agreement (target ≥85%), with a confusion table showing which theme boundaries are weak.
     *Sampling:* take **35 purely random** (unbiased estimate) **+ 15 stratified** across under-represented themes and all source types (diagnostic power). Report both separately — a purely random draw on this corpus will be dominated by `delivery_ops` and teach you little about the boundaries that matter.
  3. **Triangulation across three input types** — reviews, **the n=20 survey**, and **the 6 interviews**. High confidence requires ≥2 independent types. *(The survey is a distinct triangulation source, not just another review set.)*
  4. **Assumption & gap routing** — `[ASSUMPTION]` on speculative claims, `[VALIDATE]` on gaps, each mapped to a specific interview question.
  5. **Bias disclosure** — source skew (75% app-store), rating polarization (777 five-star vs 178 one-star), 277 items with no rating, survivorship, thin social sources.
* **⚠ Contingency if agreement < 85%**: do not hide it. Diagnose via the confusion table, sharpen the two or three conflicting theme definitions in the prompt, re-run classification (it's cheap and resumable), and re-audit. **Report both the before and after figures** — a documented improvement loop scores better than a single unexplained number.
* **Outputs**: `src/validate.py`; 50-item audit sheet; computed agreement score (**no placeholders, ever**).

---

### Phase 6: Streamlit Dashboard
* **Status**: 🔲 **PLANNED** (graded public link)
* **Objectives**: Interactive interface to navigate findings, the 8 research questions, and validation metrics.
* **Implementation**:
  1. `src/dashboard.py`.
  2. Sidebar filters: theme, research question (Q1–Q8), segment, source type.
  3. Global corpus stats, agreement score, and **prominent bias notice above the insights, not buried below them**.
  4. Ranked, expandable insight cards: opportunity score, real quotes with source links, confidence, counter-evidence, validation hook.
  5. Deploy to Streamlit Community Cloud; **verify the link opens in an incognito window** (an evaluator with no access scores you down).
* **Outputs**: `src/dashboard.py`; public URL.

---

### Phase 7: Findings Report & 1-Slider *(new — was missing)*
* **Status**: 🔲 **PLANNED** (graded deliverables)
* **Why this phase exists**: `context.md` and `architecture.md` are the **blueprint** — what you set out to build. The **results** need their own home. Without this phase, the insights live only inside code output and never become a communicable deliverable.
* **Implementation**:
  1. `docs/findingsReport.md` — theme distribution with real counts, ranked insights with quotes and URLs, the validation results (agreement %, confusion table, triangulation matrix), bias disclosure, and the Q1–Q8 answer map including any gaps.
  2. **The 1-slider** for the deck covering the four required demonstrations: how data is gathered · how themes are identified · how insights are generated · how quality was validated.
  3. Appendix pack: `labeledReviews.jsonl`, `themeSummary.csv`, `sanitize_report.txt`, audit sheet — all with open access set.
* **Outputs**: `docs/findingsReport.md`; 1-slider; linked appendix artifacts.

---

## Parallel Track: Part 2 Starts Now

**This is the biggest schedule risk in the project.** Interview recruitment has a multi-day lead time that no amount of engineering speed can compress. If Part 1 finishes on 1 Aug and interviews start then, Parts 2–4 fail.

* **Today**: message the 20 survey respondents (a warm list — they already opted in) and book 6 calls of ~20 minutes.
* **Target segment**: young working professionals / working couples, 24–35, metro, 4+ orders per month.
* **Priority probes** — drive these from the survey signals already in hand: the 13/20 who report buying identical products every time (what would break the pattern?), and the confidence-builders they selected ("reviews from shoppers like me", trial sizes).
* **The scoring artifact**: a validation matrix recording where interviews **confirmed**, **challenged**, or **killed** each LENS insight. A hypothesis the interviews killed is worth more than five they confirmed — it proves the research was real.