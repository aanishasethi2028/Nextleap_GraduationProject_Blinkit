#!/usr/bin/env python3
import os
import json
import numpy as np
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(r"c:\AS\PM\Projects\GradProject_Blinkit_P1\.env")

# Theme metadata: Addressability & Strategic Fit
THEME_SCORES = {
    "awareness_gap": {"addressability": 5.0, "strategic_fit": 5.0},
    "trust_information": {"addressability": 5.0, "strategic_fit": 5.0},
    "ux_friction": {"addressability": 4.5, "strategic_fit": 4.0},
    "mental_model": {"addressability": 4.0, "strategic_fit": 5.0},
    "price_value": {"addressability": 3.5, "strategic_fit": 3.5},
    "habit_loop": {"addressability": 3.0, "strategic_fit": 4.0},
    "trust_quality": {"addressability": 3.0, "strategic_fit": 4.0},
    "assortment_gap": {"addressability": 3.0, "strategic_fit": 4.0},
    "emotional": {"addressability": 3.0, "strategic_fit": 4.0},
    "delivery_ops": {"addressability": 2.0, "strategic_fit": 1.0},  # Quarantined
    "other": {"addressability": 1.0, "strategic_fit": 1.0}           # Quarantined
}

# Theme to Research Questions mapping
THEME_TO_RQ = {
    "habit_loop": ["Q1", "Q4"],
    "awareness_gap": ["Q3"],
    "mental_model": ["Q2"],
    "trust_quality": ["Q6"],
    "trust_information": ["Q5"],
    "price_value": ["Q6"],
    "ux_friction": ["Q3", "Q6"],
    "assortment_gap": ["Q7"],
    "emotional": ["Q2"]
}

# 8 Core Research Questions mapping descriptions
RQ_MAP = {
    "Q1": "Why do users repeatedly buy from the same categories?",
    "Q2": "What prevents users from exploring new categories?",
    "Q3": "How do users discover products today?",
    "Q4": "What role do habits play in shopping behavior?",
    "Q5": "What information do users need before trying a new category?",
    "Q6": "What frustrations emerge repeatedly?",
    "Q7": "What unmet needs emerge consistently across discussions?"
}

SYSTEM_PROMPT = """You are a Principal UX Researcher and Product Strategist.
Your task is to analyze a cluster of user feedback reviews from a quick-commerce platform and output a structured insight card as a JSON object.

The output MUST be a JSON object matching this schema exactly:
{
  "insight_title": "Clear statement of the finding, not just the topic",
  "finding": "Detailed description of the customer pain point or behavioral pattern observed in the cluster.",
  "so_what_for_growth": "Strategic implication of this finding for increasing category exploration and adoption.",
  "representative_quotes": [
    {"text": "Exact quote substring from a review", "source_url": "Matching source URL"},
    {"text": "Exact quote substring from a review", "source_url": "Matching source URL"},
    {"text": "Exact quote substring from a review", "source_url": "Matching source URL"}
  ],
  "affected_segments": ["Segment name 1", "Segment name 2"],
  "severity": 3.5, // Float between 1.0 (negligible) and 5.0 (critical blocker)
  "counter_evidence": "Any contradicting evidence, complaints, or alternative patterns in this cluster, or null if none",
  "validation_needed": "What primary research (e.g. user interviews) needs to confirm or probe further"
}

RULES:
1. Every quote in `representative_quotes` MUST be an exact substring from one of the provided reviews. Never make up or modify quotes.
2. Ensure you copy the EXACT matching `source_url` from the review object.
3. Return ONLY a valid JSON object. Do not include markdown fences, prose, or additional text.
"""

def call_llm(prompt, system_prompt):
    # Try Groq first
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        client = OpenAI(api_key=groq_key.strip(), base_url="https://api.groq.com/openai/v1")
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"Groq failed: {e}. Trying Gemini fallback...")
    
    # Try Gemini fallback
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        client = OpenAI(api_key=gemini_key.strip(), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        try:
            resp = client.chat.completions.create(
                model="models/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"Gemini failed: {e}")
            raise e
    else:
        raise ValueError("No API keys found for Groq or Gemini in environment.")

def main():
    jsonl_path = os.path.join("data", "labeledReviews.jsonl")
    san_path = os.path.join("data", "SanitizedBlinkitReviews.xlsx")
    cluster_assignments_path = os.path.join("data", "cluster_assignments.json")
    out_insights = os.path.join("data", "insights.json")

    if not all(os.path.exists(p) for p in [jsonl_path, san_path, cluster_assignments_path]):
        print("Error: Missing input files.")
        return

    # Load cluster assignments
    with open(cluster_assignments_path, "r", encoding="utf-8") as f:
        cluster_assignments = json.load(f)

    # Load review texts and URLs from Sanitized Excel
    df_san = pd.read_excel(san_path)
    id_to_text = dict(zip(df_san["id"], df_san["Reviews"]))
    id_to_url = dict(zip(df_san["id"], df_san["Source/URL"]))

    # Load review metadata from jsonl
    reviews = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            reviews.append(json.loads(line))

    # Group reviews by cluster
    clustered_reviews = {}
    for r in reviews:
        rid = r["id"]
        cluster_name = cluster_assignments.get(rid)
        if not cluster_name:
            continue
        
        # Skip quarantined clusters
        if (cluster_name.startswith("delivery_ops") or 
            cluster_name.startswith("other") or 
            cluster_name == "low_signal" or
            cluster_name == "other_small_groups"):
            continue

        if cluster_name not in clustered_reviews:
            clustered_reviews[cluster_name] = []
        
        # Attach full text and url
        r["text"] = id_to_text.get(rid, "")
        r["url"] = id_to_url.get(rid, "")
        clustered_reviews[cluster_name].append(r)

    print(f"Found {len(clustered_reviews)} valid clusters for synthesis.")

    # Sort clusters by size and select those with >= 5 reviews
    filtered_clusters = {k: v for k, v in clustered_reviews.items() if len(v) >= 5}
    print(f"Clusters with >= 5 reviews: {len(filtered_clusters)}")

    # Determine maximum frequency for normalization
    frequencies = [len(reviews) for reviews in filtered_clusters.values()]
    if not frequencies:
        print("No valid clusters found for synthesis.")
        return
    max_frequency = max(frequencies)

    insights = []
    answered_questions = set()

    for cname, creviews in sorted(filtered_clusters.items(), key=lambda x: len(x[1]), reverse=True):
        frequency = len(creviews)
        
        # Extract primary theme from cluster name (e.g. trust_quality_negative -> trust_quality)
        primary_theme = "other"
        for t in THEME_SCORES.keys():
            if cname.startswith(t):
                primary_theme = t
                break

        print(f"\nSynthesizing cluster '{cname}' (Theme: {primary_theme}, Size: {frequency})...")

        # Select up to 12 representative reviews
        # Prioritize based on review length, confidence, rating
        # For negative clusters, favor lower rating; for positive, favor higher rating.
        is_negative = "negative" in cname
        def rank_key(rev):
            rating = rev.get("rating")
            if rating is None or pd.isna(rating):
                rating_score = 3
            else:
                rating_score = int(rating)
            
            rating_priority = (5 - rating_score) if is_negative else rating_score
            length_score = len(rev.get("text", ""))
            confidence_score = rev.get("confidence", 0.5)
            return (rating_priority, confidence_score, length_score)

        sorted_reviews = sorted(creviews, key=rank_key, reverse=True)
        rep_reviews = sorted_reviews[:12]

        # Format reviews for prompt
        formatted_reviews = []
        for idx, rev in enumerate(rep_reviews):
            formatted_reviews.append({
                "n": idx + 1,
                "review_id": rev["id"],
                "text": rev["text"],
                "source_url": rev["url"],
                "rating": rev.get("rating"),
                "sentiment": rev.get("sentiment"),
                "confidence": rev.get("confidence")
            })

        prompt_data = {
            "cluster_name": cname,
            "theme": primary_theme,
            "total_reviews_in_cluster": frequency,
            "reviews": formatted_reviews
        }

        prompt = f"Analyze this cluster of user reviews:\n\n{json.dumps(prompt_data, indent=2, ensure_ascii=False)}"

        try:
            response_text = call_llm(prompt, SYSTEM_PROMPT)
            card = json.loads(response_text)
        except Exception as e:
            print(f"Error calling LLM for cluster {cname}: {e}")
            continue

        # Programmatic opportunity score calculation
        # Frequency score scaled logarithmically: 1.0 to 5.0
        freq_score = 1.0 + 4.0 * (np.log(frequency) / np.log(max_frequency))
        
        # Read severity estimated by LLM
        severity = float(card.get("severity", 3.0))
        severity = max(1.0, min(5.0, severity))  # Clamp between 1.0 and 5.0

        # Retrieve scores
        theme_meta = THEME_SCORES.get(primary_theme, {"addressability": 3.0, "strategic_fit": 3.0})
        addressability = theme_meta["addressability"]
        strategic_fit = theme_meta["strategic_fit"]

        opportunity_score = freq_score * severity * addressability * strategic_fit

        # Programmatic confidence level:
        # High confidence if >= 15 reviews AND >= 2 distinct source types
        distinct_sources = set(r.get("source_type") for r in creviews)
        if frequency >= 15 and len(distinct_sources) >= 2:
            confidence_level = "high"
        elif frequency >= 8 or len(distinct_sources) >= 2:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Map to Research Questions
        rqs = THEME_TO_RQ.get(primary_theme, ["Q2", "Q7"])
        for rq in rqs:
            answered_questions.add(rq)

        # Build final card structure
        insight_card = {
            "cluster_name": cname,
            "primary_theme": primary_theme,
            "insight_title": card.get("insight_title"),
            "finding": card.get("finding"),
            "so_what_for_growth": card.get("so_what_for_growth"),
            "opportunity_score": round(opportunity_score, 2),
            "metrics": {
                "frequency": frequency,
                "frequency_score": round(freq_score, 2),
                "severity": round(severity, 2),
                "addressability": addressability,
                "strategic_fit": strategic_fit
            },
            "representative_quotes": card.get("representative_quotes", []),
            "affected_segments": card.get("affected_segments", []),
            "confidence": confidence_level,
            "counter_evidence": card.get("counter_evidence"),
            "validation_needed": card.get("validation_needed"),
            "answers_questions": rqs
        }

        insights.append(insight_card)

    # Sort insights by Opportunity Score descending
    insights.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Identify gaps: research questions not answered by any cluster
    all_questions = set(RQ_MAP.keys())
    gaps = sorted(list(all_questions - answered_questions))
    gap_details = [{"id": q, "description": RQ_MAP[q]} for q in gaps]

    output_data = {
        "insights": insights,
        "gaps": gap_details
    }

    # Save to data/insights.json
    os.makedirs(os.path.dirname(out_insights), exist_ok=True)
    with open(out_insights, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully wrote {len(insights)} insight cards to {out_insights}")

    # Output ranking summary to console
    print("\n" + "="*50)
    print("  RANKED INSIGHT CARDS (PHASE 4)")
    print("="*50)
    for idx, card in enumerate(insights):
        print(f"#{idx+1}: {card['insight_title']}")
        print(f"    Cluster: {card['cluster_name']}")
        print(f"    Opportunity Score: {card['opportunity_score']} (Freq: {card['metrics']['frequency']}, Sev: {card['metrics']['severity']}, Addr: {card['metrics']['addressability']}, Fit: {card['metrics']['strategic_fit']})")
        print(f"    Confidence: {card['confidence'].upper()} | Answers: {card['answers_questions']}")
        print("-" * 50)

    if gaps:
        print("\nIdentified Research Gaps:")
        for gap in gap_details:
            print(f"  - {gap['id']}: {gap['description']}")

if __name__ == "__main__":
    main()
