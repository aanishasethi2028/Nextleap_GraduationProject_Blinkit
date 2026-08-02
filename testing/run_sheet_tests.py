#!/usr/bin/env python3
import os
import json
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
        return None
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
    return None

def main():
    sheet_path = os.path.join("testing", "Part1_TestingInputs.xlsx")
    json_path = os.path.join("data", "insights.json")

    print("======================================================================")
    print("           LENS PIPELINE CLASSIFICATION INTEGRITY TESTER              ")
    print("======================================================================")

    if not os.path.exists(sheet_path):
        print(f"Error: Test sheet not found at {sheet_path}")
        return
    if not os.path.exists(json_path):
        print(f"Error: Insights file not found at {json_path}")
        return

    # Load spreadsheet and JSON
    df = pd.read_excel(sheet_path)
    with open(json_path, "r", encoding="utf-8") as f:
        insights_data = json.load(f)

    insights = insights_data.get("insights", [])
    insights_by_title = {i["insight_title"].strip().lower(): i for i in insights}

    passed_count = 0
    failed_count = 0
    not_found_count = 0

    results = []

    for index, row in df.iterrows():
        sheet_idx = row["Index"]
        sheet_title = str(row["Insight Title (Card Name)"]).strip()
        expected_theme_label = str(row["Theme Selection"]).strip()
        expected_rq_desc = str(row["Mapped Research Question"]).strip()
        expected_conf = str(row["Confidence Level Selection"]).strip().upper()

        expected_theme = theme_mapping.get(expected_theme_label, expected_theme_label.lower().replace(" ", "_"))
        expected_rq = find_rq_key(expected_rq_desc)

        # Lookup in actual output JSON
        actual_insight = None
        for title, val in insights_by_title.items():
            # Check prefix or partial match
            if sheet_title.lower() in title or title in sheet_title.lower():
                actual_insight = val
                break

        if actual_insight is None:
            results.append({
                "Index": sheet_idx,
                "Title": sheet_title[:50] + "...",
                "Status": "NOT FOUND IN OUTPUT",
                "Details": "Insight title could not be matched with synthesized results."
            })
            not_found_count += 1
            continue

        actual_theme = actual_insight.get("primary_theme")
        actual_rqs = actual_insight.get("answers_questions", [])
        actual_conf = str(actual_insight.get("confidence")).strip().upper()

        errors = []
        if actual_theme != expected_theme:
            errors.append(f"Theme mismatch: expected '{expected_theme}' ({expected_theme_label}), got '{actual_theme}'")
        if expected_rq not in actual_rqs:
            errors.append(f"Research Question mismatch: expected '{expected_rq}', got '{actual_rqs}'")
        if actual_conf != expected_conf:
            errors.append(f"Confidence mismatch: expected '{expected_conf}', got '{actual_conf}'")

        if not errors:
            status = "PASSED"
            passed_count += 1
            details = "All expected attributes match."
        else:
            status = "FAILED"
            failed_count += 1
            details = " | ".join(errors)

        results.append({
            "Index": sheet_idx,
            "Title": sheet_title[:50] + "...",
            "Status": status,
            "Details": details
        })

    # Print Results Table
    df_results = pd.DataFrame(results)
    print("\n------------------------------ Detailed Results ------------------------------")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', 60)
    print(df_results[["Index", "Title", "Status", "Details"]])

    print("\n-------------------------------- Summary Report ------------------------------")
    print(f"Total Test Cases Evaluated : {len(df)}")
    print(f"Tests Passed               : {passed_count}")
    print(f"Tests Failed               : {failed_count}")
    print(f"Insights Not Found in JSON : {not_found_count}")
    print("======================================================================")

if __name__ == "__main__":
    main()
