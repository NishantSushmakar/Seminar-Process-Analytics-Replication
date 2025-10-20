#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import sys
from ast import literal_eval
from typing import Dict, List, Set, Tuple


def is_target_db(dir_name: str) -> bool:
    return dir_name.startswith("P2P-") or dir_name.startswith("ERP-")


def parse_metrics_file(file_path: str) -> Tuple[Dict[str, float], str]:
    """
    Attempt to parse a metrics file into a dict of key->value pairs.
    Returns (metrics_dict, raw_text). If parsing fails, metrics_dict will be empty.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        sys.stderr.write(f"Failed to read {file_path}: {e}\n")
        return {}, ""

    # Try JSON first
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data, text
    except Exception:
        pass

    # Try Python literal dict (as in the provided example)
    try:
        data = literal_eval(text)
        if isinstance(data, dict):
            return data, text
    except Exception:
        pass

    # Fallback: simple key: value pairs (one per line)
    metrics: Dict[str, float] = {}
    line_pattern = re.compile(r"^\s*([^:]+)\s*[:=]\s*([\-\d\.eE]+)\s*$")
    for line in text.splitlines():
        m = line_pattern.match(line)
        if not m:
            continue
        key = m.group(1).strip()
        val_str = m.group(2).strip()
        try:
            val = float(val_str)
        except ValueError:
            continue
        metrics[key] = val
    return metrics, text


def collect_metrics(base_dir: str) -> Tuple[List[Dict[str, object]], Set[str]]:
    rows: List[Dict[str, object]] = []
    all_metric_keys: Set[str] = set()

    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Base directory does not exist: {base_dir}")

    for entry in sorted(os.listdir(base_dir)):
        if not is_target_db(entry):
            continue
        db_path = os.path.join(base_dir, entry)
        if not os.path.isdir(db_path):
            continue

        new_results_dir = os.path.join(db_path, "new_results")
        if not os.path.isdir(new_results_dir):
            continue

        # Find *_METRICS.txt files
        try:
            candidate_files = [
                f for f in os.listdir(new_results_dir)
                if f.endswith("_METRICS.txt") and os.path.isfile(os.path.join(new_results_dir, f))
            ]
        except Exception:
            candidate_files = []

        for file_name in sorted(candidate_files):
            file_path = os.path.join(new_results_dir, file_name)
            metrics, raw = parse_metrics_file(file_path)

            row: Dict[str, object] = {
                "database": entry,
                "metric_file": file_name,
            }

            if metrics:
                for k, v in metrics.items():
                    # Ensure numeric values are kept as numbers where possible
                    row[k] = v
                all_metric_keys.update(metrics.keys())
            else:
                # If nothing parsed, store raw text for debugging
                row["raw_content"] = raw
                all_metric_keys.add("raw_content")

            rows.append(row)

    return rows, all_metric_keys


def write_csv(rows: List[Dict[str, object]], metric_keys: Set[str], out_path: str) -> None:
    # Stable, readable ordering
    preferred_order = [
        "precision",
        "recall",
        "f1",
        "relaxed_precision",
        "relaxed_recall",
        "relaxed_f1",
        "textual_precision",
        "textual_recall",
        "textual_f1",
    ]
    remaining_keys = [k for k in sorted(metric_keys) if k not in preferred_order]
    header = ["database", "metric_file"] + [k for k in preferred_order if k in metric_keys] + remaining_keys

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in header})


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge *_METRICS.txt from P2P-* and ERP-* into a CSV")
    default_base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "testDBs"))
    parser.add_argument("--base-dir", default=default_base, help="Root directory containing P2P-* and ERP-* folders (default: %(default)s)")
    parser.add_argument("--out", default=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "plots", "merged_metrics.csv")), help="Output CSV path (default: %(default)s)")
    args = parser.parse_args()

    rows, keys = collect_metrics(args.base_dir)
    if not rows:
        sys.stderr.write("No metrics found. Ensure folders like P2P-* or ERP-* contain new_results with *_METRICS.txt files.\n")
        # Still write an empty file with just headers
        write_csv([], set(), args.out)
        print(f"Wrote empty CSV to {args.out}")
        return

    write_csv(rows, keys, args.out)
    print(f"Merged {len(rows)} metric files into {args.out}")


if __name__ == "__main__":
    main()


