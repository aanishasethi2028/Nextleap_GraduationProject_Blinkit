# Blinkit LENS (Listening ENgine for Shoppers) - Project Reference Manual

This document provides a comprehensive technical overview of the **Blinkit LENS** pipeline, detailing data gathering, sanitization statistics, theme classifications, research question mappings, programmatic scoring, and the UX Director agreement audit.

---

## 📊 1. Data Ingestion & Sanitization Pipeline

The pipeline ingests raw user feedback from multiple channels and processes it to filter out noise, leaving high-signal data for LLM analysis.

### Raw Data Count: 1,327
* **Source Dataset**: Loaded from the raw spreadsheet `data/SanitozedReport.xlsx` containing **1,327 rows**.

### Step-by-Step Sanitization:
1. **Whitespace Cleaning**: Collapse all contiguous spaces and trim margins.
2. **Blank Filtering**: Drop any rows where the review column is empty.
3. **Exact Deduplication (17 Removed)**: Run a duplicate removal script targeting exact review text matches.
   * *Formula*: $1,327 \text{ raw rows} - 17 \text{ duplicates} = 1,310 \text{ unique reviews}$.
4. **Low-Signal Filtering (55 Flagged)**: Scans each review to count letters (covering both Latin `[a-zA-Z]` and Devanagari `[\u0900-\u097F]`). Reviews with **fewer than 10 letters** (e.g., short words like `"Blinkit ok"`, emoji-only strings like `"🛵🚀👍"`, or numbers) are flagged as low-signal.
5. **High-Signal Insights Dataset (1,255)**:
   * *Formula*: $1,310 \text{ unique reviews} - 55 \text{ low-signal reviews} = 1,255 \text{ usable rich reviews}$.

### Source Channel Breakdown:
* **Google Play Store**: 500 reviews
* **Apple App Store**: 487 reviews
* **YouTube Comments**: 277 reviews
* **MouthShut**: 41 reviews
* **Trustpilot**: 4 reviews
* **Reddit**: 1 review
* **Total unique reviews**: 1,310

---

## 🏷️ 2. Theme Definitions

LENS groups user reviews into 8 primary strategic themes. Each review is classified into exactly one theme:

| Theme | Key Focus & Semantic Boundaries |
| :--- | :--- |
| **`habit_loop`** | Convenience-led habitual usage; relying on Blinkit as a daily grocery shopping companion. |
| **`price_value`** | Fair price perception, handling charges, delivery fees, and coupon/discount appreciation. |
| **`ux_friction`** | App interface glitches, navigation difficulties, checkout issues, and feature requests. |
| **`trust_quality`** | Freshness of groceries, quality of vegetables/fruits, packaging, and refund systems. |
| **`mental_model`** | Traditional grocery stores (Kirana, D-Mart) vs. transition to quick-commerce routines. |
| **`awareness_gap`** | User unawareness that Blinkit stocks specialized/non-grocery categories. |
| **`assortment_gap`** | Demand for a wider catalog (e.g., missing specific brands, series of books, etc.). |
| **`emotional`** | Joy of instant delivery, feeling of security, and social/delivery agent appreciation. |

---

## ❓ 3. Research Questions (RQs) Mapping

The project maps customer insights back to 7 core intelligence pillars to outline the customer journey:

* **Q1: Consumer Intent** – *"What prompts the very first quick-commerce order in a household?"*
* **Q2: Behavioral Transition** – *"How do users transition from emergency top-ups to routine basket ordering?"*
* **Q3: Category Resistance** – *"What categories do users explicitly resist buying on quick commerce?"*
* **Q4: Trust Divergence** – *"How does user trust differ between fresh groceries and packaged goods?"*
* **Q5: Information Barrier** – *"What information (reviews, specifications) do users need before trying a new category?"*
* **Q6: UX Friction** – *"What app interface elements cause friction during category exploration?"*
* **Q7: Habitual Emotion** – *"What is the emotional role of quick commerce in the user's daily habit loop?"*

---

## 📈 4. Programmatic Opportunity Score

To prioritize findings, each insight card is assigned an **Opportunity Score** calculated mathematically:

$$\text{Opportunity Score} = \text{Frequency Score} \times \text{Severity} \times \text{Addressability} \times \text{Strategic Fit}$$

* **Frequency Score**: Scaled logarithmically from 1.0 to 5.0 based on the cluster's review count:
  $$\text{Freq Score} = 1.0 + 4.0 \times \left(\frac{\ln(\text{Frequency})}{\ln(\text{Max Frequency})}\right)$$
* **Severity**: Pain level (1.0 to 5.0) estimated by the LLM during review analysis.
* **Addressability & Strategic Fit**: Strategic multipliers (1.0 to 5.0) mapped per theme.

---

## 📐 5. Confidence Triangulation Calibration

Confidence thresholds (HIGH, MEDIUM, LOW) are programmatically assigned by checking for support in the quantitative shopper survey ($n=50$):

* **HIGH Confidence**: Backed by **LENS Reviews** and **Direct Survey Validation** (e.g. `habit_loop`, `price_value` themes).
* **MEDIUM Confidence**: Backed by **LENS Reviews** with **Partial/Secondary Survey Support** (e.g. `ux_friction`, `trust_quality` themes).
* **LOW Confidence**: Backed solely by **LENS Reviews** (e.g. `awareness_gap`, `assortment_gap`).

---

## 🔬 6. Human-LLM Agreement & Semantic Confusion Matrix

To audit and validate classification boundaries, a sample of 50 reviews (35 random, 15 stratified) was cross-checked against a Ground Truth UX UXR Director.

### Baseline vs. Sharpened Model:
* **Baseline Classifier (`Llama-3.1-8B-instant`)**:
  * **Overall Agreement**: **56.0%**
  * *Diagnosis*: Struggled with Hinglish slang, often misclassifying general praise as `trust_quality` and convenience stories as `delivery_ops`.
* **Sharpened Classifier (`Llama-3.3-70B-versatile` + Prompts)**:
  * **Overall Agreement**: **60.0%** (Stratified Agreement: **66.7%**, Random Agreement: **57.1%**)
  * *Diagnosis*: Swapping to the 70B model and sharpening theme boundaries resolved empty predictions and clarified Hinglish boundaries. Remaining overlaps occur on compound reviews (e.g., speed + price in one sentence).

### Semantic Confusion Matrix (After Sharpening):
Rows represent the **Expert Auditor (Ground Truth)**, and Columns represent the **Sharpened LLM Classifier**:

| Expert / LLM | habit_loop | awareness_gap | mental_model | trust_quality | trust_info | price_value | ux_friction | assortment_gap | delivery_ops | emotional | other |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **habit_loop** | **3** | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| **awareness_gap**| 0 | **2** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **mental_model** | 0 | 0 | **4** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **trust_quality**| 0 | 0 | 0 | **6** | 0 | 0 | 1 | 1 | 1 | 0 | 0 |
| **trust_info**   | 0 | 0 | 0 | 0 | **0** | 0 | 0 | 0 | 0 | 0 | 0 |
| **price_value**  | 0 | 0 | 0 | 0 | 0 | **7** | 0 | 0 | 0 | 0 | 0 |
| **ux_friction**  | 0 | 0 | 0 | 1 | 0 | 0 | **8** | 0 | 0 | 0 | 0 |
| **assortment_gap**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2** | 0 | 0 | 0 |
| **delivery_ops** | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | **12**| 0 | 0 |
| **emotional**    | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| **other**        | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
