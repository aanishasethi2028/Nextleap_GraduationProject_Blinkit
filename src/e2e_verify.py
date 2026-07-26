#!/usr/bin/env python3
import os
import json
import pandas as pd
import subprocess
import sys

def check_file(path, check_fn, label):
    print(f"Checking {label} ({path})...")
    if not os.path.exists(path):
        print(f"  [FAIL] Failed: File does not exist!")
        return False
    try:
        ok, msg = check_fn(path)
        if ok:
            print(f"  [OK] Passed: {msg}")
            return True
        else:
            print(f"  [FAIL] Failed: {msg}")
            return False
    except Exception as e:
        print(f"  [FAIL] Failed with exception: {e}")
        return False

def check_sanitized_xlsx(path):
    df = pd.read_excel(path)
    rows = len(df)
    cols = list(df.columns)
    expected_cols = ["id", "Reviews", "Rating", "Source/URL", "source_type", "is_low_signal", "review_len"]
    missing = [c for c in expected_cols if c not in cols]
    if missing:
        return False, f"Missing columns: {missing}"
    if rows != 1310:
        return False, f"Expected 1310 rows, got {rows}"
    return True, f"1310 rows, columns: {cols}"

def check_sanitize_report(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "Raw rows in file" not in content or "Unique reviews (final)" not in content:
        return False, "Report is missing key ingestion text metrics"
    return True, "Contains correct sanitization metrics"

def check_labeled_jsonl(path):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            if "id" not in data or "primary_theme" not in data:
                return False, f"Line {i+1} is missing required fields (id, primary_theme)"
            count += 1
    if count != 1310:
        return False, f"Expected 1310 labeled rows, got {count}"
    return True, f"1310 labeled records verified"

def check_theme_summary(path):
    df = pd.read_csv(path)
    if "primary_theme" not in df.columns or "count" not in df.columns:
        return False, "Missing required columns in theme summary"
    total_count = df["count"].sum()
    if total_count != 1310:
        return False, f"Expected sum of theme counts to be 1310, got {total_count}"
    return True, f"Sum of themes is 1310"

def check_cluster_assignments(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    total_mapped = len(data)
    if total_mapped != 1310:
        return False, f"Expected 1310 mapped IDs, got {total_mapped}"
    clusters = set(data.values())
    return True, f"Mapped {total_mapped} IDs across {len(clusters)} distinct clusters"

def check_insights_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "insights" not in data or "gaps" not in data:
        return False, "Missing 'insights' or 'gaps' keys in insights.json"
    insights_count = len(data["insights"])
    gaps_count = len(data["gaps"])
    if insights_count != 17:
        return False, f"Expected 17 growth insights, got {insights_count}"
    if gaps_count != 2:
        return False, f"Expected 2 quarantined gaps (Q5 and Q7), got {gaps_count}"
    return True, f"Discovered 17 growth insights and 2 gaps (Q5, Q7)"

def check_survey_xlsx(path):
    df = pd.read_excel(path)
    rows = len(df)
    if rows != 42:
        return False, f"Expected 42 survey respondents, got {rows}"
    return True, f"n=42 actual respondents verified"

def check_audit_sheet(path):
    df = pd.read_excel(path)
    rows = len(df)
    if rows != 50:
        return False, f"Expected 50 audit reviews, got {rows}"
    cols = list(df.columns)
    if "new_sharpened_theme" not in cols:
        return False, "Missing 'new_sharpened_theme' improvement loop column"
    return True, f"50 reviews with sharpened metrics: {cols}"

def check_validation_report_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "before_audit" not in data or "after_audit" not in data:
        return False, "Missing 'before_audit' or 'after_audit' keys"
    before_score = data["before_audit"]["overall_agreement_pct"]
    after_score = data["after_audit"]["overall_agreement_pct"]
    return True, f"Audit loop verified: Before={before_score:.1f}% -> After={after_score:.1f}%"

def check_validation_report_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "HUMAN-LLM AGREEMENT AUDIT" not in content or "CONFUSION TABLE" not in content:
        return False, "Missing agreement or matrix tables"
    return True, "Contains agreement loop and confusion matrices"

def check_script_syntax(filepath):
    print(f"Checking syntax of {filepath}...")
    try:
        res = subprocess.run([sys.executable, "-m", "py_compile", filepath], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  [OK] Passed compilation")
            return True
        else:
            print(f"  [FAIL] Compilation failed: {res.stderr}")
            return False
    except Exception as e:
        print(f"  [FAIL] Compilation check failed with exception: {e}")
        return False

def main():
    print("==========================================================")
    st_title = "  LENS SYSTEM END-TO-END INTEGRITY VERIFICATION  "
    print(st_title)
    print("==========================================================")
    
    scripts = [
        "sanitizeReviews.py",
        "classifyReviews.py",
        "src/clustering.py",
        "src/synthesis.py",
        "src/validate.py",
        "src/re_audit.py",
        "src/dashboard.py"
    ]
    
    all_ok = True
    for s in scripts:
        if not check_script_syntax(s):
            all_ok = False
            
    print("\n------------------ Checking Output Files ------------------")
    
    files_to_check = [
        ("SanitizedBlinkitReviews.xlsx", check_sanitized_xlsx, "Sanitized Review Sheet"),
        ("data/sanitize_report.txt", check_sanitize_report, "Sanitization Report Log"),
        ("labeledReviews.jsonl", check_labeled_jsonl, "LLM Labeled Corpus"),
        ("themeSummary.csv", check_theme_summary, "Theme Distribution CSV"),
        ("data/cluster_assignments.json", check_cluster_assignments, "Semantic Clusters Mapping"),
        ("data/insights.json", check_insights_json, "Ranked Growth Insights & Gaps"),
        ("data/Actual_Quick-Commerce Insights Survey.xlsx", check_survey_xlsx, "Actual Triangulation Survey"),
        ("data/audit_sheet.xlsx", check_audit_sheet, "Human-Agreement Audit Sample"),
        ("data/validation_report.json", check_validation_report_json, "Validation JSON metrics"),
        ("data/validation_report.txt", check_validation_report_txt, "Validation Report Text")
    ]
    
    for path, check_fn, label in files_to_check:
        if not check_file(path, check_fn, label):
            all_ok = False
            
    print("\n------------------ Running Edge Case Tests ------------------")
    try:
        res = subprocess.run([sys.executable, "src/test_edge_cases.py"], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode == 0:
            print("  [OK] Programmatic Edge-Case Tests passed!")
        else:
            print(f"  [FAIL] Programmatic Edge-Case Tests failed:\n{res.stderr}")
            all_ok = False
    except Exception as e:
        print(f"  [FAIL] Failed to run programmatic edge case tests: {e}")
        all_ok = False

    print("==========================================================")
    if all_ok:
        print("  [SUCCESS] ALL LENS SYSTEM INTEGRITY VERIFICATION PASSED SUCCESSFULLY!  ")
    else:
        print("  [FAIL] SOME VERIFICATION CHECKS FAILED. Please review the errors above.  ")
    print("==========================================================")

if __name__ == "__main__":
    main()
