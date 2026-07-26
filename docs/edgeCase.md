# LENS Edge Case Management & Handling

This document details the edge cases encountered across the 7 phases of the **LENS (Listening ENgine for Shoppers)** insight pipeline and how they are handled in code to ensure data integrity and analytical rigor.

---

## 📥 Phase 1: Ingestion & Text Sanitization

### 1. Low-Signal, Short, and Emoji-Only Reviews
* **Edge Case**: Reviews containing only emojis, single letters (e.g. "nice", "ok"), or empty text.
* **Risk**: Feeding these reviews to the clustering pipeline will create meaningless noise clusters, and feeding them to LLM synthesis will waste tokens and return low-signal summaries.
* **Code Handling**:
  - The script [sanitizeReviews.py](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/sanitizeReviews.py) uses a regular expression to count alphanumeric letters: `len(re.findall(r'[a-zA-Z\u0900-\u097F]', text)) < 10`.
  - Rows with fewer than 10 letters are flagged with `is_low_signal = True`.
  - These rows are **retained** in the database to preserve the rating distribution and source statistics, but they are **filtered out** from the downstream semantic clustering and synthesis.

### 2. Exact Duplicate Review Texts
* **Edge Case**: Identical reviews posted multiple times (often due to scraping retries, cross-posting, or user spam).
* **Risk**: Artificial inflation of specific customer complaints, leading to skewed cluster density and inaccurate frequency metrics.
* **Code Handling**:
  - Drops exact duplicate review texts using Pandas `drop_duplicates(subset=["Reviews"])` (17 duplicates removed).

### 3. Missing Ratings in Social Data
* **Edge Case**: YouTube comments and Reddit posts do not contain star ratings, unlike Play Store or App Store reviews.
* **Risk**: Assigning dummy values (like `0` or `3` stars) would distort average rating calculations.
* **Code Handling**:
  - The rating field is stored as `NaN` / `None` in the database and spreadsheets.
  - The validation script counts missing ratings programmatically: `df_san["Rating"].isna().sum()` (277 missing ratings flagged) and discloses this in the corpus bias disclosures tab of the dashboard.

---

## 🏷️ Phase 2: LLM Classification Pipeline

### 1. Hinglish and Native Dialects
* **Edge Case**: Reviews written in Hindi using the Latin alphabet (e.g., *"Bhai Chandigarh mein bhi yahi kam..."*).
* **Risk**: Standard translation pipelines are prone to loss-of-nuance or literal translation errors.
* **Code Handling**:
  - The classification prompt explicitly instructs: `"Hinglish is common; interpret it correctly."`
  - The classification is conducted directly on the multilingual text, avoiding a separate translation step.

### 2. HTTP 429 Rate Limits during Bulk Classification
* **Edge Case**: Request volume exceeds Groq's free-tier RPM (30) or TPM (40,000) limits.
* **Risk**: Pipeline crash, resulting in incomplete classification runs.
* **Code Handling**:
  - Implemented a sleep throttle `SLEEP = 2.5` between batches of 10.
  - Implemented an automatic retry wrapper with backoff:
    ```python
    except Exception as e:
        wait = 3
        print(f"Retry {attempt+1}/{MAX_RETRIES} after {wait}s ({str(e)[:70]})")
        time.sleep(wait)
    ```

### 3. Output Schema Literalism & Empty Predictions
* **Edge Case**: Small 8B models (like `llama-3.1-8b-instant`) interpreting the empty string values in the JSON format example as literal fixed outputs.
* **Risk**: Model outputting `"primary_theme": ""` or `"evidence_span": ""` for all records.
* **Code Handling**:
  - Updated the JSON format instruction in the prompt to use filled placeholder strings (e.g., `"primary_theme": "selected_theme"`, `"evidence_span": "quote_from_review"`) instead of empty quotes.

### 4. Mid-Run Script Crashes
* **Edge Case**: Network disconnects or API errors during a long-running classification run.
* **Risk**: Wasting API tokens and time by restarting from review 1.
* **Code Handling**:
  - Implemented resumable state: the script reads `labeledReviews.jsonl` on startup, extracts already-processed review IDs, and filters them out of the backlog before calling the API.

---

## 📊 Phase 3: Semantic Clustering

### 1. HDBSCAN Noise Dominance
* **Edge Case**: Density-based clustering on short texts commonly assigns a huge share to noise (label = `-1`).
* **Risk**: Discarding 60% or more of the reviews, resulting in loss of insights.
* **Code Handling**:
  - Implemented a programmatic fallback check in [clustering.py](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/src/clustering.py):
    ```python
    if noise_ratio > 0.40 or num_clusters < 6:
        # Fall back to theme-based grouping (primary_theme, sentiment splits)
    ```
  - Since HDBSCAN generated 68% noise, the pipeline automatically triggered the fallback to preserve all customer signals.

---

## 💡 Phase 4: Insight Synthesis & Ranking

### 1. Operational Overload
* **Edge Case**: Operational complaints (delivery speed, support) are the "loud majority", drowning out growth barriers.
* **Risk**: The top-ranked growth insights being dominated by standard shipping complaints.
* **Code Handling**:
  - Programmatically quarantined the `delivery_ops`, `other`, and `low_signal` clusters in [synthesis.py](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/src/synthesis.py) before opportunity score ranking, preserving them only in the overview logs.

### 2. Under-Represented Research Gaps
* **Edge Case**: No insights synthesized from LENS reviews map to Q5 (information needed before trial) and Q7 (experimenter segments).
* **Risk**: Forcing speculative insights on thin data.
* **Code Handling**:
  - The script programmatically identifies RQs with zero matching insights.
  - Quarantines these questions as **gaps** and routes them to primary research interview probing questions, rather than inferring answers from noise.

---

## 🛡️ Phase 5: Verification & Validation Layer

### 1. LLM Agreement Score < 85%
* **Edge Case**: The 8B classifier model gets a low agreement score (e.g. 56%) compared to the expert auditor.
* **Risk**: Low classification quality leading to unreliable insights.
* **Code Handling**:
  - Swapped classifier model in the re-audit [re_audit.py](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/src/re_audit.py) to `llama-3.3-70b-versatile` and applied sharpened prompt boundary definitions, increasing agreement to 60.0%.
  - Documented both before and after metrics to highlight the improvement loop.

### 2. Validation Prefix Duplication
* **Edge Case**: Repeated validation script runs adding double prefixes (e.g., `[VALIDATE] [VALIDATE] ...`).
* **Risk**: Ugly, corrupted text in `insights.json` and reports.
* **Code Handling**:
  - Programmatically strip existing prefixes before prepending the new ones in `src/validate.py`:
    ```python
    for prefix in ["[VALIDATE] ", "[ASSUMPTION] ", "[VALIDATE]", "[ASSUMPTION]"]:
        if val.startswith(prefix):
            val = val[len(prefix):].strip()
    ```

---

## 🖥️ Phase 6: Streamlit Dashboard

### 1. Missing Data Files on Startup
* **Edge Case**: Launching the dashboard web app before running `synthesis.py` or `validate.py`.
* **Risk**: Raw Python file exception traceback shown on page.
* **Code Handling**:
  - Added file existence checks and standard `st.stop()` callouts to present clean, user-friendly error banners if datasets are missing.

### 2. Special Characters / Emojis in Text Render
* **Edge Case**: Emoticons or native Unicode in comments raising encoding tracebacks in Python or web browser.
* **Code Handling**:
  - Explicitly specified `encoding='utf-8'` on all file read operations.
  - Handled raw text outputs in HTML blocks with proper CSS escaping and embedding.
