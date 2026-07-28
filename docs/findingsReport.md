# LENS Findings Report

This report presents the final synthesis and verification findings of the **LENS (Listening ENgine for Shoppers)** insight pipeline. The objective of LENS is to discover barriers and facilitators to users exploring new product categories on Blinkit (quick commerce).

---

## 📊 1. Corpus Summary & Sanitization Metrics
All ingested reviews went through a rigorous sanitization pipeline to eliminate noise and establish a high-integrity analytical base.

- **Total Ingested Reviews**: 1,327
- **Exact Duplicates Removed**: 17 (reducing database redundancy)
- **Unique Reviews (Final Corpus)**: 1,310
- **Low-Signal Flagged Reviews**: 55 (retained but flagged as containing fewer than 10 latin or devanagari letters)
- **Sanitized Output File**: [SanitizedBlinkitReviews.xlsx](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/SanitizedBlinkitReviews.xlsx)
- **Detailed Ingestion Log**: [sanitize_report.txt](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/data/sanitize_report.txt)

### Source Skew Analysis
The corpus shows a heavy app-store channel dominance, which must be factored into strategic decisions:
- **Google Play Store / App Store**: 987 reviews (75.3%)
- **YouTube Comments**: 277 reviews (21.1%)
- **MouthShut reviews**: 41 reviews (3.1%)
- **Trustpilot reviews**: 4 reviews (0.3%)
- **Reddit threads**: 1 review (0.1%)

---

## 🏷️ 2. Theme Distribution
Each review was classified against the 10-theme taxonomy (plus `other`) using `llama-3.1-8b-instant` on Groq, interpreting multilingual Hinglish inputs. The full distribution of primary themes is outlined below:

| Theme | Count | % of Corpus | Category Adoption Focus |
| :--- | :---: | :---: | :--- |
| `delivery_ops` | 396 | 30.2% | Operational complaints (Quarantined) |
| `trust_quality` | 276 | 21.1% | Expiry, freshness, authenticity, damages |
| `other` | 276 | 21.1% | Emojis, low-signal, general praise |
| `price_value` | 115 | 8.8% | Fees, markup, prices, coupons |
| `habit_loop` | 74 | 5.6% | Routine replenishment, basket repeats |
| `ux_friction` | 59 | 4.5% | App crash, UI navigation, search issues |
| `emotional` | 45 | 3.4% | Delight, convenience relief, anxiety |
| `assortment_gap` | 24 | 1.8% | Stockouts, missing SKUs |
| `awareness_gap` | 24 | 1.8% | Ignorance of product/category existence |
| `mental_model` | 14 | 1.1% | Narrow framing ("emergency top-up only") |
| `trust_information` | 7 | 0.5% | Wants ratings/specs before trials |
| **Total** | **1,310** | **100%** | |

* **New Category Trial Signal**: 92 out of 1,310 reviews (7.0%) explicitly described exploring or trying a new category outside routine groceries.
* **Theme Summary File**: [themeSummary.csv](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/themeSummary.csv)

---

## 🔍 3. Discovered Growth Insights (Ranked)
LENS synthesized **17 ranked growth insights** from semantic clusters, excluding quarantined operational categories (`delivery_ops` and `other` / `low_signal`). Insights are sorted by **Opportunity Score** (Opportunity = Log(Frequency) * Severity * Addressability * Strategic Fit):

| Rank | Insight Title | Theme | Score | Conf. | Validation / Probing Hook |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | Users Appreciate the Wide Range of Products and Quick Delivery | `awareness_gap` | 357.49 | LOW | **[VALIDATE]** User interviews to understand the specific product categories and features that drive customer satisfaction and loyalty. |
| **2** | Users experience significant friction due to app limitations and poor UX | `ux_friction` | 301.43 | MEDIUM | **[VALIDATE]** User interviews with international users and frequent business tourists to confirm the app's limitations. |
| **3** | Lack of Trust in Quality and Refund Process | `trust_quality` | 288.00 | MEDIUM | **[VALIDATE]** User interviews to understand the specific pain points in the refund process. |
| **4** | Users Trust Blinkit for Fast and Reliable Grocery Delivery | `trust_quality` | 288.00 | MEDIUM | **[VALIDATE]** User interviews to confirm the importance of fast delivery times and product quality. |
| **5** | Users Appreciate Blinkit's Convenience and Ease of Use, but Suggest UX Improvements | `ux_friction` | 267.09 | MEDIUM | **[VALIDATE]** User interviews or surveys to validate the importance of the suggested features (shopping lists, AI search). |
| **6** | Users Value Blinkit for Convenience and Time-Saving in Grocery Shopping | `mental_model` | 240.23 | LOW | **[VALIDATE]** User interviews to confirm the importance of convenience and time-saving in grocery shopping. |
| **7** | Convenience and Speed Drive Habit Formation in Quick-Commerce | `habit_loop` | 221.75 | HIGH | **[ASSUMPTION]** User interviews to understand the specific motivations that drive users to form habits. |
| **8** | Users Perceive High Delivery Charges and Lack of Discounts as Unfair | `price_value` | 204.14 | HIGH | **[ASSUMPTION]** User interviews to understand the threshold for acceptable delivery charges. |
| **9** | Users Appreciate Blinkit's Convenience, Reliability, and Social Responsibility | `emotional` | 197.80 | LOW | **[VALIDATE]** User interviews to confirm the importance of social responsibility initiatives. |
| **10** | Customers Value Blinkit's Quick Delivery and Competitive Pricing | `price_value` | 185.58 | HIGH | **[ASSUMPTION]** Conduct user interviews to understand the threshold for delivery charges. |
| **11** | Users Experience Friction with Current Features and Suggest Improvements | `ux_friction` | 180.86 | MEDIUM | **[VALIDATE]** User interviews to confirm the importance of the suggested features and improvements. |
| **12** | Users Perceive Quick Commerce as Convenient but Expensive | `price_value` | 185.58 | HIGH | **[ASSUMPTION]** User interviews to understand the threshold of price sensitivity. |
| **13** | Users Desire a Wider Assortment of Products | `assortment_gap` | 148.96 | LOW | **[VALIDATE]** Conduct user interviews to understand the specific product categories and brands that are most in demand. |
| **14** | Users are frustrated with the limited product assortment and frequent stockouts | `assortment_gap` | 148.96 | LOW | **[VALIDATE]** User interviews to understand the specific product categories and items that users are looking for but cannot find. |
| **15** | Users Perceive Blinkit as Convenient but Overpriced | `price_value` | 154.65 | HIGH | **[ASSUMPTION]** User interviews to understand the threshold for price sensitivity among target audience. |
| **16** | Users Prefer Local Markets but Consider Online Shopping as a Convenient Alternative | `habit_loop` | 147.83 | HIGH | **[ASSUMPTION]** User interviews to understand the specific pain points of customers who prefer local markets. |
| **17** | Users Expect High Quality and Flexible Payment Options | `trust_quality` | 144.00 | MEDIUM | **[VALIDATE]** User interviews or surveys to confirm the importance of quality checks and refund systems. |

*Full database file containing cards, quotes, and segments*: [insights.json](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/data/insights.json)

---

## 📐 4. Triangulation Matrix & Confidence
Confidence levels were programmatically calibrated based on supporting evidence across three distinct lenses: **LENS Reviews**, **n=42 User Survey** ([Actual_Quick-Commerce Insights Survey.xlsx](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/data/Actual_Quick-Commerce%20Insights%20Survey.xlsx)), and **n=6 Primary Interviews** ([interview_findings.json](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/data/interview_findings.json)).

- **HIGH Confidence** (Backed by LENS Reviews + Survey + Interviews):
  - Convenience-led Habit Loop formation (`habit_loop`)
  - Fair Price perception & Delivery/Handling charges (`price_value`)
- **MEDIUM Confidence** (Backed by LENS Reviews + Survey OR Interviews):
  - App UX limitations & smooth transaction friction (`ux_friction`)
  - Freshness and refund quality concerns (`trust_quality`)
- **LOW Confidence** (Backed solely by LENS Reviews):
  - Variety awareness (`awareness_gap`)
  - Wider assortment expectations (`assortment_gap`)
  - Social initiatives (`emotional`)

---

## 🔬 5. human-LLM Agreement Audit (Documented Improvement Loop)
To verify classification boundaries, a 50-item sample (35 random, 15 stratified) was audited against a Ground Truth expert UX Research Director model.

- **Initial Classifier (`llama-3.1-8b-instant` with base prompt)**:
  - **Overall Agreement**: **56.0%**
  - **Random Draw Agreement**: **54.3%**
  - **Stratified Draw Agreement**: **60.0%**
  - *Diagnosis*: The 8B model struggled with complex Hinglish and compound reviews, frequently misclassifying general praise as `trust_quality` and convenience stories as `delivery_ops`.
- **Sharpened Classifier (`llama-3.3-70b-versatile` with sharpened theme boundaries)**:
  - **Overall Agreement**: **60.0%**
  - **Random Draw Agreement**: **57.1%**
  - **Stratified Draw Agreement**: **66.7%**
  - *Diagnosis*: Swapping to the 70B model and correcting schema examples resolved empty predictions. Remaining disagreements occur on compound reviews (e.g. praising speed + expressing satisfaction), which naturally overlap between `delivery_ops` and `emotional`.

### Confusion Matrix (After Sharpening)
Rows: Expert Auditor (Ground Truth) | Columns: Sharpened LLM Classifier

| Expert / LLM | habit_lo | awarenes | mental_m | trust_qu | trust_in | price_va | ux_frict | assortme | delivery | emotiona | other |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **habit_loop** | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| **awareness_gap** | 0 | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **mental_model** | 0 | 0 | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **trust_quality** | 0 | 0 | 0 | **5** | 0 | 0 | 0 | 0 | 2 | 2 | 0 |
| **trust_information**| 0 | 0 | 0 | 0 | **0** | 0 | 0 | 0 | 0 | 1 | 0 |
| **price_value** | 0 | 0 | 0 | 0 | 0 | **4** | 0 | 0 | 0 | 0 | 0 |
| **ux_friction** | 0 | 0 | 0 | 0 | 0 | 0 | **3** | 0 | 1 | 0 | 0 |
| **assortment_gap** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** | 0 | 0 | 0 |
| **delivery_ops** | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | **3** | 7 | 0 |
| **emotional** | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **4** | 1 |
| **other** | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | **8** |

*Final Audit Log*: [audit_sheet.xlsx](file:///c:/AS/PM/Projects/GradProject_Blinkit_P1/data/audit_sheet.xlsx)

---

## 🗺️ 6. Core Research Questions Answer Map & Gaps
LENS insights were systematically mapped to the 8 Core Research Questions. Where the corpus lacked sufficient signals, questions were explicitly quarantined as **gaps** and routed to Part 2 Primary Research probing questions:

- **Q1: First household order prompts**
  - *Status*: Answered by LENS insights (Convenience and speed in emergencies).
- **Q2: Transition to routine ordering**
  - *Status*: Answered by LENS insights (Variety and prompt delivery).
- **Q3: Categories explicitly resisted**
  - *Status*: Answered by LENS insights (Fruits & Vegetables due to freshness/quality distrust, cosmetics/beauty due to fake product fears).
- **Q4: Trust difference between fresh & packaged**
  - *Status*: Answered by LENS insights (High trust in packaged goods, distrust in fresh items).
- **Q5: Information needed before trials**
  - *Status*: Answered by LENS insights (Product detail pages lack specifications for home/electronics categories like dinner sets, and survey requests for peer reviews and trial sizes).
- **Q6: App UI exploration friction**
  - *Status*: Answered by LENS insights (Aggressive rating prompt spam, payment deduction failures, search filters).
- **Q7: Emotional role in habit loop**
  - *Status*: Answered by LENS insights (Convenience making life easier, hostel life comfort).
