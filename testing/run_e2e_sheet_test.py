#!/usr/bin/env python3
import os
import json
import shutil
import pandas as pd

theme_mapping = {
    "Habit Loop": "habit_loop",
    "Awareness Gap": "awareness_gap",
    "Mental Model": "mental_model",
    "Trust Quality": "trust_quality",
    "Trust Information": "trust_information",
    "Price Value": "price_value",
    "UX Friction": "ux_friction",
    "Assortment Gap": "assortment_gap",
    "Delivery Ops": "delivery_ops",
    "Emotional": "emotional",
    "Other": "other"
}

rq_labels = {
    "Q1": "What prompts the very first quick-commerce order in a household?",
    "Q2": "How do users transition from emergency top-ups to routine basket ordering?",
    "Q3": "What categories do users explicitly resist buying on quick commerce?",
    "Q4": "How does user trust differ between fresh groceries and packaged goods?",
    "Q5": "What information (reviews, specifications) do users need before trying a new category?",
    "Q6": "What app interface elements cause friction during category exploration?",
    "Q7": "What is the emotional role of quick commerce in the user's daily habit loop?"
}

def find_rq_key(sheet_rq):
    if not isinstance(sheet_rq, str):
        return "Q2"
    sheet_rq_clean = sheet_rq.strip().lower()
    # Check for direct key match
    if sheet_rq_clean.upper() in rq_labels:
        return sheet_rq_clean.upper()
    # Match against descriptions
    for q_key, q_desc in rq_labels.items():
        q_desc_clean = q_desc.lower()
        if sheet_rq_clean in q_desc_clean or q_desc_clean in sheet_rq_clean:
            return q_key
        # Check partial prefix
        if len(sheet_rq_clean) >= 15 and (sheet_rq_clean[:15] in q_desc_clean or q_desc_clean[:15] in sheet_rq_clean):
            return q_key
    return "Q2"

def main():
    sheet_path = os.path.join("testing", "Part1_TestingInputs.xlsx")
    json_path = os.path.join("data", "insights.json")
    backup_path = os.path.join("data", "insights.json.bak")

    if not os.path.exists(sheet_path):
        print(f"Error: Test inputs file not found at {sheet_path}")
        return

    # Backup original insights.json
    if os.path.exists(json_path) and not os.path.exists(backup_path):
        shutil.copyfile(json_path, backup_path)
        print("Backed up original insights.json to insights.json.bak")

    # Load spreadsheet
    df = pd.read_excel(sheet_path)
    
    mock_insights = []
    
    # Iterate through all 25 rows
    for index, row in df.iterrows():
        title = str(row["Insight Title (Card Name)"]).strip()
        theme_label = str(row["Theme Selection"]).strip()
        rq_desc = str(row["Mapped Research Question"]).strip()
        conf_label = str(row["Confidence Level Selection"]).strip().lower()
        
        theme_key = theme_mapping.get(theme_label, theme_label.lower().replace(" ", "_"))
        rq_key = find_rq_key(rq_desc)
        
        # Calculate a mock score descending from 350 to keep ordering neat
        mock_score = 350.0 - (index * 8.5)
        
        # Structure a full insight card
        insight_card = {
            "cluster_name": f"{theme_key}_mock_cluster_{index+1}",
            "primary_theme": theme_key,
            "insight_title": title,
            "finding": f"This represents findings for theme '{theme_label}' answering research question '{rq_desc[:40]}...'. It is generated from the user's Part1_TestingInputs sheet.",
            "so_what_for_growth": f"Develop product strategies tailored to {theme_label} to unlock category adoption and expansion.",
            "opportunity_score": round(mock_score, 2),
            "metrics": {
                "frequency": int(30 - index),
                "frequency_score": round(3.5 + (index * 0.05), 2),
                "severity": 4.0,
                "addressability": 4.0,
                "strategic_fit": 4.0
            },
            "representative_quotes": [
                {
                    "text": f"Quote for test case #{index+1} regarding {title[:40]}...",
                    "source_url": "Google Play Store"
                }
            ],
            "affected_segments": [
                "Target Category Shoppers",
                f"{theme_label} segment"
            ],
            "confidence": conf_label,
            "counter_evidence": None,
            "validation_needed": f"[VALIDATE] Perform target group interviews to validate the findings of test case #{index+1}.",
            "answers_questions": [rq_key]
        }
        mock_insights.append(insight_card)

    output_data = {
        "insights": mock_insights,
        "gaps": []
    }

    # Write temporary insights.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated temporary insights.json with {len(mock_insights)} test cases from the spreadsheet.")

if __name__ == "__main__":
    main()
