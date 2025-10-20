#!/usr/bin/env python3
"""
Script to merge all F1 metric CSV files from best_new_plots folder into a single comprehensive dataset.
The script includes normal f1, relaxed_f1, and textual_f1 metrics organized by prompt and version.
"""

import pandas as pd
import os
import glob
from collections import defaultdict
import numpy as np

def main():
    # Define the path to the best_new_plots folder
    plots_folder = "best_new_plots"

    # Define the metric types and their corresponding file patterns
    metric_types = ['f1', 'relaxed_f1', 'textual_f1']

    # Find all metric CSV files
    all_files = {}
    for metric in metric_types:
        pattern = os.path.join(plots_folder, f"*-plot-data-{metric}.csv")
        files = glob.glob(pattern)
        all_files[metric] = files
        print(f"Found {len(files)} {metric} CSV files:")
        for file in files:
            print(f"  - {file}")

    # Dictionary to store all data organized by dataset
    # Structure: {dataset: {version: {prompt: {metric: score}}}}
    dataset_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    # Process each metric type
    for metric in metric_types:
        print(f"\nProcessing {metric} files...")

        for file_path in all_files[metric]:
            # Extract dataset name from filename (e.g., "BPI2016" from "BPI2016-plot-data-f1.csv")
            filename = os.path.basename(file_path)
            dataset_name = filename.split(f"-plot-data-{metric}.csv")[0]

            print(f"  Processing {dataset_name} {metric}...")

            # Read the CSV file
            df = pd.read_csv(file_path)

            # Process each row in the file
            for _, row in df.iterrows():
                folder = row['Folder']
                prompt = int(row['Prompt'])
                score = float(row['f1'])  # All files use 'f1' as the column name

                # Extract version from folder name (e.g., "V1" from "BPI2016-V1")
                version = folder.split('-')[-1]  # Gets the last part after splitting by '-'

                # Store the data
                dataset_data[dataset_name][version][prompt][metric] = score

            print(f"    Processed {len(df)} records for {dataset_name} {metric}")

    # Define the expected structure
    datasets = ["BPI2016", "ERP", "P2P", "UWV"]
    versions = ["V1", "V2", "V3"]
    prompts = [1, 2, 3, 4, 5, 6, 7]

    # Create separate DataFrames for each dataset
    dataset_dfs = []

    for dataset in datasets:
        # Create column headers: Dataset, Prompt, then for each version: V1_f1, V1_relaxed_f1, V1_textual_f1, etc.
        columns = ["Dataset", "Prompt"]
        for version in versions:
            for metric in metric_types:
                columns.append(f"{version}_{metric}")

        # Create rows for each prompt
        dataset_rows = []
        for prompt in prompts:
            row = [dataset, f"Prompt_{prompt}"]

            # Add all metric scores for each version
            for version in versions:
                for metric in metric_types:
                    # Get the metric score, use NaN if not available
                    score = dataset_data[dataset][version].get(prompt, {}).get(metric, np.nan)
                    row.append(score)

            dataset_rows.append(row)

        # Create DataFrame for this dataset
        dataset_df = pd.DataFrame(dataset_rows, columns=columns)
        dataset_dfs.append(dataset_df)

    # Combine all dataset DataFrames
    merged_df = pd.concat(dataset_dfs, ignore_index=True)

    # Display the merged data
    print("\n" + "="*80)
    print("MERGED F1 SCORES DATASET")
    print("="*80)
    print(merged_df.to_string(index=False))

    # Save to CSV
    output_file = "merged_f1_scores.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"\n✅ Merged dataset saved to: {output_file}")

    # Print summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)

    # Get all metric columns (excluding Dataset and Prompt)
    metric_columns = [col for col in merged_df.columns if col not in ['Dataset', 'Prompt']]

    total_cells = len(datasets) * len(prompts) * len(versions) * len(metric_types)
    missing_cells = merged_df[metric_columns].isna().sum().sum()
    filled_cells = total_cells - missing_cells

    print(f"Total expected data points: {total_cells}")
    print(f"Filled data points: {filled_cells}")
    print(f"Missing data points: {missing_cells}")
    print(f"Coverage: {(filled_cells/total_cells)*100:.1f}%")

    # Show missing data by dataset
    print("\nMissing data by dataset:")
    for dataset in datasets:
        dataset_rows = merged_df[merged_df['Dataset'] == dataset]
        missing_count = dataset_rows[metric_columns].isna().sum().sum()
        total_points = len(prompts) * len(versions) * len(metric_types)
        print(f"  {dataset}: {missing_count}/{total_points} missing ({(missing_count/total_points)*100:.1f}%)")

    # Show missing data by metric type
    print("\nMissing data by metric type:")
    for metric in metric_types:
        metric_cols = [col for col in metric_columns if col.endswith(f"_{metric}")]
        missing_count = merged_df[metric_cols].isna().sum().sum()
        total_points = len(datasets) * len(prompts) * len(versions)
        print(f"  {metric}: {missing_count}/{total_points} missing ({(missing_count/total_points)*100:.1f}%)")

    # Show which specific prompt-version-metric combinations are missing
    print("\nDetailed missing data analysis:")
    for dataset in datasets:
        dataset_rows = merged_df[merged_df['Dataset'] == dataset]

        missing_found = False
        for _, row in dataset_rows.iterrows():
            prompt = row['Prompt']
            for version in versions:
                for metric in metric_types:
                    col_name = f"{version}_{metric}"
                    if pd.isna(row[col_name]):
                        if not missing_found:
                            print(f"\n{dataset} missing data:")
                            missing_found = True
                        print(f"  - {prompt} {col_name}")

        if not missing_found:
            print(f"\n{dataset}: No missing data")

if __name__ == "__main__":
    main()