#!/usr/bin/env python3
import os
import glob
import argparse
import pandas as pd
from typing import List, Dict, Set


BASE_PROMPTS = [
    '01-baseline',
    '02-persona',
    '03-few-shot-example',
    '04-chain-of-thought',
    '05-tree-of-thought',
    '06-processmining-knowledge',
]

PROMPT07_BY_DB: Dict[str, str] = {
    'P2P': '07-RunningExample',
    'ERP': '07-paperj',
    'UWV': '07-UWV',
    'BPI2016': '07-BPI2016',
}


def expected_prompts_for_database(database_name: str) -> List[str]:
    db_family = str(database_name).split('-')[0]
    prompt07 = PROMPT07_BY_DB.get(db_family)
    prompts = list(BASE_PROMPTS)
    if prompt07:
        prompts.append(prompt07)
    return prompts


def merge_best_new_plots(best_new_plots_dir: str, out_path: str) -> None:
    pattern = os.path.join(best_new_plots_dir, '*-table-all_runs.csv')
    files = sorted(glob.glob(pattern))
    if not files:
        pd.DataFrame(columns=['Database','Prompt','Error']).to_csv(out_path, index=False)
        print(f"Found 0 inputs; wrote empty CSV to {out_path}")
        return

    frames: List[pd.DataFrame] = []
    for f in files:
        try:
            df = pd.read_csv(f)
            frames.append(df)
        except Exception as e:
            print(f"Warning: Failed to read {f}: {e}")

    if not frames:
        pd.DataFrame(columns=['Database','Prompt','Error']).to_csv(out_path, index=False)
        print(f"No readable inputs; wrote empty CSV to {out_path}")
        return

    # Union columns across all frames
    all_columns: Set[str] = set()
    for df in frames:
        all_columns.update(df.columns.tolist())

    # Ensure canonical columns present
    all_columns.update(['Database','Prompt','Error'])

    # Reindex frames to the union of columns
    frames = [df.reindex(columns=sorted(all_columns)) for df in frames]

    merged = pd.concat(frames, ignore_index=True, sort=False)

    # Normalize NaNs in canonical columns
    for col in ['Database','Prompt','Error']:
        if col not in merged.columns:
            merged[col] = ''
    merged['Database'] = merged['Database'].fillna('')
    merged['Prompt'] = merged['Prompt'].fillna('')
    merged['Error'] = merged['Error'].fillna('')

    # Add placeholders for missing prompts per database
    metric_cols: List[str] = [c for c in merged.columns if c not in ['Database','Prompt','Error']]
    rows_to_add: List[Dict[str, object]] = []
    for database, group in merged.groupby('Database', dropna=False):
        expected = set(expected_prompts_for_database(database))
        present = set(str(p) for p in group['Prompt'].tolist())
        missing = expected - present
        for pr in sorted(missing):
            placeholder = { 'Database': database, 'Prompt': pr, 'Error': 'Error' }
            for mc in metric_cols:
                placeholder[mc] = ''
            rows_to_add.append(placeholder)

    if rows_to_add:
        merged = pd.concat([merged, pd.DataFrame(rows_to_add)], ignore_index=True, sort=False)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    merged.to_csv(out_path, index=False)
    print(f"Merged {len(files)} files into {out_path} with {len(rows_to_add)} placeholder rows added.")


def main() -> None:
    parser = argparse.ArgumentParser(description='Merge per-DB all_runs tables from best_new_plots into one CSV with placeholders for missing prompts.')
    default_in = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'best_new_plots'))
    default_out = os.path.abspath(os.path.join(default_in, 'AllDBs-table-all_runs.csv'))
    parser.add_argument('--in-dir', default=default_in, help='Directory containing *-table-all_runs.csv files (default: %(default)s)')
    parser.add_argument('--out', default=default_out, help='Output CSV path (default: %(default)s)')
    args = parser.parse_args()

    merge_best_new_plots(args.in_dir, args.out)


if __name__ == '__main__':
    main()


