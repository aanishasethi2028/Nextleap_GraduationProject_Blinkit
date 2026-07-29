#!/usr/bin/env python3
import os
import re
import pandas as pd

def is_low_signal(text):
    # Count Latin (a-z) and Devanagari (\u0900-\u097F) letters
    letters = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text))
    return letters < 10

def get_source_type(url):
    u = str(url).lower()
    if "youtube" in u or "youtu.be" in u:
        return "youtube"
    if "play" in u or "google play store" in u:
        return "playstore"
    if "app store" in u or "apps.apple" in u or "appstore" in u:
        return "appstore"
    if "mouthshut" in u:
        return "mouthshut"
    if "trustpilot" in u:
        return "trustpilot"
    if "reddit" in u:
        return "reddit"
    return "other"

def main():
    raw_path = os.path.join("data", "SanitozedReport.xlsx")
    out_xlsx = os.path.join("data", "SanitizedBlinkitReviews.xlsx")
    out_report = os.path.join("data", "sanitize_report.txt")
    out_txtx = os.path.join("data", ".txtx")

    if not os.path.exists(raw_path):
        print(f"Error: Raw file {raw_path} not found.")
        return

    # Load raw
    df = pd.read_excel(raw_path)
    raw_count = len(df)

    # Clean text: collapse whitespace and trim
    df = df.dropna(subset=["Reviews"])
    df["Reviews"] = df["Reviews"].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x).strip())
    df = df[df["Reviews"] != ""]
    clean_count = len(df)

    # Drop exact duplicates on review text, keeping the first occurrence
    df_unique = df.drop_duplicates(subset=["Reviews"], keep="first").copy()
    dup_removed = clean_count - len(df_unique)
    final_count = len(df_unique)

    # Derive source_type
    df_unique["source_type"] = df_unique["Source/URL"].apply(get_source_type)

    # Flag low signal
    df_unique["is_low_signal"] = df_unique["Reviews"].apply(is_low_signal)
    low_signal_count = df_unique["is_low_signal"].sum()
    usable_count = final_count - low_signal_count

    # Calculate review length
    df_unique["review_len"] = df_unique["Reviews"].apply(len)

    # Assign stable IDs: R0001 to R1310
    df_unique.insert(0, "id", [f"R{i+1:04d}" for i in range(final_count)])

    # Output columns: id, Source/URL, source_type, Reviews, Rating, review_len, is_low_signal
    df_output = df_unique[["id", "Source/URL", "source_type", "Reviews", "Rating", "review_len", "is_low_signal"]]

    # Save to Excel
    df_output.to_excel(out_xlsx, index=False)
    print(f"Sanitized file written to {out_xlsx}")

    # Generate Report Content
    report_lines = [
        "Sanitization Report",
        "===================",
        f"Raw rows in file             : {raw_count}",
        f"After removing blanks        : {clean_count}",
        f"Duplicates removed           : {dup_removed}",
        f"Unique reviews (final)       : {final_count}",
        f"Low-signal (emoji/too short) : {low_signal_count}  (kept, flagged is_low_signal=True)",
        f"Usable rich reviews          : {usable_count}",
        "",
        "Source breakdown:",
        df_output["source_type"].value_counts().to_string(),
        "",
        "Rating distribution:",
        df_output["Rating"].value_counts(dropna=False).to_string()
    ]
    report_text = "\n".join(report_lines) + "\n"

    # Save reports
    with open(out_report, "w", encoding="utf-8") as f:
        f.write(report_text)
    with open(out_txtx, "w", encoding="utf-8") as f:
        f.write(report_text)

    print("Sanitization report written successfully.")

if __name__ == "__main__":
    main()
