#!/usr/bin/env python3
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import hdbscan

def main():
    jsonl_path = os.path.join("data", "labeledReviews.jsonl")
    san_path = os.path.join("data", "SanitizedBlinkitReviews.xlsx")
    out_dir = "data"
    out_json = os.path.join(out_dir, "cluster_assignments.json")
    out_summary = os.path.join(out_dir, "clustering_summary.txt")

    if not os.path.exists(jsonl_path) or not os.path.exists(san_path):
        print("Error: Input files labeledReviews.jsonl or SanitizedBlinkitReviews.xlsx are missing.")
        return

    # Load review texts and is_low_signal flag from SanitizedBlinkitReviews.xlsx
    df_san = pd.read_excel(san_path)
    id_to_text = dict(zip(df_san["id"], df_san["Reviews"]))
    id_to_low_signal = dict(zip(df_san["id"], df_san["is_low_signal"]))

    # Load reviews metadata from JSONL
    reviews = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            reviews.append(json.loads(line))

    print(f"Loaded {len(reviews)} reviews from {jsonl_path}.")

    # Exclude low-signal reviews from primary embedding/clustering
    rich_reviews = [r for r in reviews if not id_to_low_signal.get(r["id"], False)]
    print(f"Rich reviews for clustering: {len(rich_reviews)}")

    # Use evidence span if available and valid, fallback to full review text
    texts = []
    for r in rich_reviews:
        span = r.get("evidence_span")
        if span and span != "(classification failed)" and span != "(low-signal)":
            texts.append(span)
        else:
            texts.append(id_to_text.get(r["id"], ""))

    ids = [r["id"] for r in rich_reviews]

    # Generate embeddings
    print("Generating embeddings via all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=False)
    print(f"Embeddings generated. Shape: {embeddings.shape}")

    # Run HDBSCAN
    min_cluster_size = 15
    min_samples = 5
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)

    unique_labels = set(labels)
    hdbscan_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    noise_count = (labels == -1).sum()
    noise_pct = noise_count / len(labels) * 100

    print(f"HDBSCAN Results: {hdbscan_clusters} clusters, {noise_count}/{len(labels)} noise items ({noise_pct:.1f}%)")

    # Determine if fallback is needed: noise > 40% or fewer than 6 clusters
    use_fallback = noise_pct > 40.0 or hdbscan_clusters < 6

    cluster_assignments = {}
    summary_lines = []

    if use_fallback:
        print("\n[FALLBACK TRIGGERED] HDBSCAN noise exceeds 40% or generated < 6 clusters.")
        print("Falling back to theme-based grouping (grouped by primary_theme + sentiment).")
        
        summary_lines.append("Clustering Method: Theme-based Grouping (HDBSCAN Fallback)")
        summary_lines.append(f"Reason: HDBSCAN noise was {noise_pct:.1f}% (> 40%) and clusters were {hdbscan_clusters} (< 6)")
        
        # Group rich reviews by primary_theme and sentiment
        fallback_groups = {}
        for r in rich_reviews:
            theme = r.get("primary_theme", "other")
            sentiment = r.get("sentiment", "neutral")
            
            # Sub-split large themes by segment or sentiment
            group_key = f"{theme}_{sentiment}"
            if group_key not in fallback_groups:
                fallback_groups[group_key] = []
            fallback_groups[group_key].append(r["id"])

        # Filter out groups with very small size to avoid clutter (e.g. size < 3), and place them in 'other_small_groups'
        final_groups = {}
        small_group_ids = []
        for gkey, r_ids in fallback_groups.items():
            if len(r_ids) >= 3:
                final_groups[gkey] = r_ids
            else:
                small_group_ids.extend(r_ids)
        
        if small_group_ids:
            final_groups["other_small_groups"] = small_group_ids

        # Map low signal items to a low signal group
        low_signal_ids = [r["id"] for r in reviews if id_to_low_signal.get(r["id"], False)]
        if low_signal_ids:
            final_groups["low_signal"] = low_signal_ids

        # Build assignment mapping
        for gkey, r_ids in final_groups.items():
            for rid in r_ids:
                cluster_assignments[rid] = gkey

        summary_lines.append(f"Total Clusters/Groups: {len(final_groups)}")
        summary_lines.append("\nGroup Counts:")
        for gkey, r_ids in sorted(final_groups.items(), key=lambda x: len(x[1]), reverse=True):
            summary_lines.append(f"  {gkey}: {len(r_ids)} reviews")
            
    else:
        print("\n[HDBSCAN SUCCESSFUL] HDBSCAN clustering meets criteria.")
        summary_lines.append("Clustering Method: HDBSCAN")
        summary_lines.append(f"HDBSCAN Clusters: {hdbscan_clusters}")
        summary_lines.append(f"Noise items: {noise_count} ({noise_pct:.1f}%)")
        
        # Map low signal reviews to cluster -2
        low_signal_ids = [r["id"] for r in reviews if id_to_low_signal.get(r["id"], False)]
        
        for rid, label in zip(ids, labels):
            cluster_assignments[rid] = int(label)
        for rid in low_signal_ids:
            cluster_assignments[rid] = -2  # Low signal marker

        summary_lines.append("\nCluster Counts:")
        counts = pd.Series(list(cluster_assignments.values())).value_counts()
        for label, count in counts.items():
            summary_lines.append(f"  Cluster {label}: {count} reviews")

    # Cluster-label convergence check (print cross-tab of assignments vs primary_theme)
    # This exposes fuzzy boundaries as requested in the plan
    print("\nRunning cluster-label convergence check...")
    cross_tab = {}
    for r in reviews:
        rid = r["id"]
        theme = r.get("primary_theme", "other")
        cluster = cluster_assignments.get(rid, "unassigned")
        if cluster not in cross_tab:
            cross_tab[cluster] = {}
        cross_tab[cluster][theme] = cross_tab[cluster].get(theme, 0) + 1

    summary_lines.append("\n" + "="*50)
    summary_lines.append("Cluster-Label Convergence Check (Cross-Tabulation)")
    summary_lines.append("="*50)
    for cluster, themes in sorted(cross_tab.items()):
        summary_lines.append(f"Cluster: {cluster}")
        for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
            summary_lines.append(f"  - Theme '{theme}': {count} reviews")

    # Write output JSON mapping
    os.makedirs(out_dir, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(cluster_assignments, f, indent=2, ensure_ascii=False)
    print(f"Cluster assignments written to {out_json}")

    # Write summary report
    summary_text = "\n".join(summary_lines) + "\n"
    with open(out_summary, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"Clustering summary written to {out_summary}")

if __name__ == "__main__":
    main()
