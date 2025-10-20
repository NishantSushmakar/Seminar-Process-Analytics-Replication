#!/usr/bin/env python3
"""
SQL File Comparison Script

This script compares all *_SQL.txt files between 'best_new_results' and 'results' folders
across all databases in the testDBs directory. It provides detailed analysis of differences
and generates comprehensive reports.
"""

import os
import glob
import difflib
import re
from pathlib import Path
from collections import defaultdict
import csv
from datetime import datetime

class SQLComparator:
    def __init__(self, testdbs_path="testDBs"):
        self.testdbs_path = testdbs_path
        self.databases = []
        self.comparison_results = defaultdict(list)
        self.summary_stats = {
            'total_databases': 0,
            'total_comparisons': 0,
            'identical_files': 0,
            'different_files': 0,
            'missing_files': 0
        }

    def discover_databases(self):
        """Find all database directories with both results and best_new_results folders."""
        print("🔍 Discovering databases...")

        for item in os.listdir(self.testdbs_path):
            db_path = os.path.join(self.testdbs_path, item)
            if os.path.isdir(db_path) and not item.startswith('.'):
                results_path = os.path.join(db_path, 'results')
                best_results_path = os.path.join(db_path, 'best_new_results')

                if os.path.exists(results_path) and os.path.exists(best_results_path):
                    self.databases.append({
                        'name': item,
                        'path': db_path,
                        'results_path': results_path,
                        'best_results_path': best_results_path
                    })
                    print(f"  ✅ Found: {item}")
                else:
                    print(f"  ⚠️  Skipped: {item} (missing required folders)")

        self.summary_stats['total_databases'] = len(self.databases)
        print(f"\n📊 Found {len(self.databases)} databases to compare")

    def extract_file_info(self, filename):
        """Extract run_id, prompt_id, and prompt_name from filename."""
        # Pattern: {run_id}_prompt-{prompt_id}-{prompt_name}.txt_SQL.txt
        pattern = r'(\d+)_prompt-(\d+)-(.+?)\.txt_SQL\.txt'
        match = re.match(pattern, filename)

        if match:
            return {
                'run_id': match.group(1),
                'prompt_id': match.group(2),
                'prompt_name': match.group(3),
                'base_name': f"prompt-{match.group(2)}-{match.group(3)}"
            }
        return None

    def find_sql_files(self, db_info):
        """Find and organize SQL files for a database."""
        results_files = {}
        best_files = {}

        # Find files in results folder
        results_pattern = os.path.join(db_info['results_path'], '*_SQL.txt')
        for file_path in glob.glob(results_pattern):
            filename = os.path.basename(file_path)
            file_info = self.extract_file_info(filename)
            if file_info:
                base_name = file_info['base_name']
                if base_name not in results_files:
                    results_files[base_name] = []
                results_files[base_name].append({
                    'path': file_path,
                    'filename': filename,
                    'info': file_info
                })

        # Find files in best_new_results folder
        best_pattern = os.path.join(db_info['best_results_path'], '*_SQL.txt')
        for file_path in glob.glob(best_pattern):
            filename = os.path.basename(file_path)
            file_info = self.extract_file_info(filename)
            if file_info:
                base_name = file_info['base_name']
                if base_name not in best_files:
                    best_files[base_name] = []
                best_files[base_name].append({
                    'path': file_path,
                    'filename': filename,
                    'info': file_info
                })

        return results_files, best_files

    def normalize_sql(self, sql_content):
        """Normalize SQL content for better comparison."""
        # Remove extra whitespace and normalize formatting
        lines = []
        for line in sql_content.split('\n'):
            # Strip whitespace and normalize
            cleaned_line = ' '.join(line.strip().split())
            if cleaned_line:  # Skip empty lines
                lines.append(cleaned_line)
        return '\n'.join(lines)

    def compare_sql_content(self, file1_path, file2_path):
        """Compare two SQL files and return detailed diff information."""
        try:
            with open(file1_path, 'r', encoding='utf-8') as f1:
                content1 = f1.read()
            with open(file2_path, 'r', encoding='utf-8') as f2:
                content2 = f2.read()

            # Normalize content for comparison
            norm_content1 = self.normalize_sql(content1)
            norm_content2 = self.normalize_sql(content2)

            # Check if identical
            is_identical = norm_content1 == norm_content2

            # Generate detailed diff
            diff = list(difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"results/{os.path.basename(file1_path)}",
                tofile=f"best_new_results/{os.path.basename(file2_path)}",
                lineterm=''
            ))

            # Calculate similarity percentage
            similarity = difflib.SequenceMatcher(None, norm_content1, norm_content2).ratio()

            return {
                'is_identical': is_identical,
                'similarity': similarity,
                'diff': diff,
                'content1': content1,
                'content2': content2,
                'norm_content1': norm_content1,
                'norm_content2': norm_content2
            }

        except Exception as e:
            return {
                'error': str(e),
                'is_identical': False,
                'similarity': 0.0,
                'diff': [],
                'content1': '',
                'content2': ''
            }

    def compare_database(self, db_info):
        """Compare all SQL files for a single database."""
        print(f"\n🔍 Comparing database: {db_info['name']}")

        results_files, best_files = self.find_sql_files(db_info)

        # Get all unique base names (prompt types)
        all_base_names = set(results_files.keys()) | set(best_files.keys())

        db_results = []

        for base_name in sorted(all_base_names):
            results_list = results_files.get(base_name, [])
            best_list = best_files.get(base_name, [])

            if not results_list and best_list:
                # File only in best_new_results
                for best_file in best_list:
                    result = {
                        'database': db_info['name'],
                        'base_name': base_name,
                        'status': 'only_in_best',
                        'results_file': None,
                        'best_file': best_file['filename'],
                        'comparison': None
                    }
                    db_results.append(result)
                    self.summary_stats['missing_files'] += 1
                    print(f"  📄 {base_name}: Only in best_new_results ({best_file['filename']})")

            elif results_list and not best_list:
                # File only in results
                for results_file in results_list:
                    result = {
                        'database': db_info['name'],
                        'base_name': base_name,
                        'status': 'only_in_results',
                        'results_file': results_file['filename'],
                        'best_file': None,
                        'comparison': None
                    }
                    db_results.append(result)
                    self.summary_stats['missing_files'] += 1
                    print(f"  📄 {base_name}: Only in results ({results_file['filename']})")

            else:
                # Files exist in both folders - compare them
                # For simplicity, compare the first file from each folder
                # (in practice, you might want to compare all combinations)
                results_file = results_list[0]
                best_file = best_list[0]

                comparison = self.compare_sql_content(results_file['path'], best_file['path'])

                result = {
                    'database': db_info['name'],
                    'base_name': base_name,
                    'status': 'compared',
                    'results_file': results_file['filename'],
                    'best_file': best_file['filename'],
                    'comparison': comparison
                }
                db_results.append(result)
                self.summary_stats['total_comparisons'] += 1

                if comparison['is_identical']:
                    self.summary_stats['identical_files'] += 1
                    print(f"  ✅ {base_name}: Identical")
                else:
                    self.summary_stats['different_files'] += 1
                    similarity_pct = comparison['similarity'] * 100
                    print(f"  🔄 {base_name}: Different (similarity: {similarity_pct:.1f}%)")

        self.comparison_results[db_info['name']] = db_results
        return db_results

    def generate_console_report(self):
        """Generate a detailed console report."""
        print("\n" + "="*80)
        print("📊 SQL FILE COMPARISON REPORT")
        print("="*80)

        print(f"📈 Summary Statistics:")
        print(f"  Total databases: {self.summary_stats['total_databases']}")
        print(f"  Total comparisons: {self.summary_stats['total_comparisons']}")
        print(f"  Identical files: {self.summary_stats['identical_files']}")
        print(f"  Different files: {self.summary_stats['different_files']}")
        print(f"  Missing files: {self.summary_stats['missing_files']}")

        if self.summary_stats['total_comparisons'] > 0:
            identical_pct = (self.summary_stats['identical_files'] / self.summary_stats['total_comparisons']) * 100
            print(f"  Identical rate: {identical_pct:.1f}%")

        print("\n🔍 Detailed Analysis by Database:")

        for db_name, results in self.comparison_results.items():
            print(f"\n📁 {db_name}:")

            different_files = [r for r in results if r['status'] == 'compared' and not r['comparison']['is_identical']]
            identical_files = [r for r in results if r['status'] == 'compared' and r['comparison']['is_identical']]
            missing_files = [r for r in results if r['status'] in ['only_in_best', 'only_in_results']]

            print(f"  📊 Summary: {len(identical_files)} identical, {len(different_files)} different, {len(missing_files)} missing")

            if different_files:
                print(f"  🔄 Different files:")
                for result in different_files:
                    similarity = result['comparison']['similarity'] * 100
                    print(f"    - {result['base_name']}: {similarity:.1f}% similar")

                    # Show a sample of the differences
                    diff_lines = result['comparison']['diff']
                    if diff_lines:
                        print(f"      Sample differences:")
                        for i, line in enumerate(diff_lines[:5]):  # Show first 5 diff lines
                            if line.startswith('+') or line.startswith('-'):
                                print(f"        {line.rstrip()}")
                        if len(diff_lines) > 5:
                            print(f"        ... and {len(diff_lines) - 5} more differences")

            if missing_files:
                print(f"  ⚠️  Missing files:")
                for result in missing_files:
                    print(f"    - {result['base_name']}: {result['status']}")

    def save_csv_report(self, filename="sql_comparison_report.csv"):
        """Save comparison results to CSV file."""
        print(f"\n💾 Saving CSV report to: {filename}")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'database', 'base_name', 'status', 'results_file', 'best_file',
                'is_identical', 'similarity_percent', 'has_differences'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for db_name, results in self.comparison_results.items():
                for result in results:
                    row = {
                        'database': result['database'],
                        'base_name': result['base_name'],
                        'status': result['status'],
                        'results_file': result['results_file'] or '',
                        'best_file': result['best_file'] or '',
                        'is_identical': '',
                        'similarity_percent': '',
                        'has_differences': ''
                    }

                    if result['comparison']:
                        row['is_identical'] = result['comparison']['is_identical']
                        row['similarity_percent'] = f"{result['comparison']['similarity'] * 100:.1f}"
                        row['has_differences'] = not result['comparison']['is_identical']

                    writer.writerow(row)

        print(f"✅ CSV report saved successfully")

    def run_comparison(self):
        """Run the complete comparison process."""
        print("🚀 Starting SQL file comparison...")

        # Discover databases
        self.discover_databases()

        if not self.databases:
            print("❌ No databases found to compare")
            return

        # Compare each database
        for db_info in self.databases:
            self.compare_database(db_info)

        # Generate reports
        self.generate_console_report()
        self.save_csv_report()

        print(f"\n🎉 Comparison complete! Check the CSV report for detailed results.")

def main():
    """Main function to run the SQL comparison."""
    comparator = SQLComparator()
    comparator.run_comparison()

if __name__ == "__main__":
    main()