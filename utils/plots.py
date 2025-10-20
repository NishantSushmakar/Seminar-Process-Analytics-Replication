'''
    Description: script to generate one parallel coordinate
    chart per DB considering all available versions.
'''
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
import numpy as np

def plot_parallel_coordinates(path_to_dbs, db_name, metric, relaxed):
    data = []
    parent_folder = path_to_dbs

    for folder in os.listdir(parent_folder):
        if folder.startswith(db_name):
            folder_path = os.path.join(parent_folder, folder, 'best_new_results')
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('_METRICS.txt'):
                        parts = file.split('_')
                        prompt_name = parts[1] # Extract prompt name
                        file_path = os.path.join(folder_path, file)
                        try:
                            with open(file_path, 'r') as f:
                                file_content = f.read().strip()
                                if file_content and file_content != '{}':
                                    file_content = file_content.replace("'", '"')
                                    metrics = json.loads(file_content)
                                    metric_key = relaxed + metric
                                    if metric_key in metrics:
                                        metric_value = metrics[metric_key]
                                        data.append({
                                            'Folder': folder,
                                            'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                            metric: metric_value
                                        })
                                    else:
                                        print(f"Warning: {file_path} missing key '{metric_key}'")
                                else:
                                    print(f"Warning: {file_path} is empty or contains empty dict.")
                            f.close()
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in file {file_path}: {e}")
                        except Exception as e:
                            print(f"Unexpected error processing file {file_path}: {e}")

    df = pd.DataFrame(data)

    # Rename string values to comply with the paper
    df['Folder']=df['Folder'].replace({
        'P2P-V03': 'P2P-V1',
        'P2P-V15': 'P2P-V2',
        'P2P-V63': 'P2P-V3',
        'ERP-V019': 'ERP-V1',
        'ERP-V209': 'ERP-V2',
        'ERP-V511': 'ERP-V3',
        'BPI2016-V07':'BPI2016-V1',
        'BPI2016-V24':'BPI2016-V2',
        'BPI2016-V31':'BPI2016-V3',
        'UWV-V06':'UWV-V1',
        'UWV-V22':'UWV-V2',
        'UWV-V31':'UWV-V3'
        })
    
    df['Prompt']=df['Prompt'].replace({
        '01-baseline':                '1',
        '02-persona':                 '2',
        '03-few-shot-example':        '3',
        '04-chain-of-thought':        '4',
        '05-tree-of-thought':         '5',
        '06-processmining-knowledge': '6',
        '07-RunningExample':          '7',
        '07-paperj':                  '7',
        '07-BPI2016':                 '7',
        '07-UWV':                     '7',
        })

    plot_metric=metric
    metric_replace = {
        'f1': 'F1-score',
        'relaxed-f1': 'F1-score',
        'textual-f1': 'F1-score'
        }
    for key in metric_replace.keys():
        plot_metric = plot_metric.replace(key, metric_replace[key])


    # Calculate average metric values if multiple runs have occurred
    df = df.groupby(['Folder','Prompt']).mean()
    df.reset_index(inplace=True)
    df.set_index('Folder')

    # Pivot the DataFrame to have folders as rows and prompt names as columns
    pivot_df = df.pivot(index='Prompt', columns='Folder', values=metric)

    # Fill NaN values with -1
    pivot_df = pivot_df.fillna(-0.2)

    # Define line styles for accessibility
    patterns = ['\\\\','','////']

    # Plot figures as bar charts
    plt.figure(figsize=(12, 6))
    ax = pivot_df.plot.bar(rot=0, zorder=100, fill=False)
    bars = ax.patches

    hatches=[]

    for j in range(pivot_df.shape[1]):
        for _ in range(pivot_df.shape[0]):
            hatches.append(patterns[j])

    for bar,hatch in zip(bars,hatches):
         bar.set_hatch(hatch)

    fontsize=36
    fontname='Times New Roman'

    # Adjust feature names (x-axis labels) 
    plt.xticks(range(len(pivot_df.index)), pivot_df.index[0:], fontsize=fontsize, fontname=fontname)

    # Adjust other font properties
    plt.xlabel('Prompts', fontsize=fontsize, fontname=fontname, visible=False)
    plt.ylabel(plot_metric, fontsize=fontsize, fontname=fontname, visible=False)

    # Set y-axis increments from -0.2 to 1.0 and replace -0.2 by
    # infinite to represent the Error generating the SQL
    ax = plt.gca()

    ax.set_yticks(np.arange(-0.2, 1.01, 0.2))
    y_labels = ax.get_yticks().tolist()
    y_labels = ['−∞' if label == -0.2 else f'{label:.1f}' for label in y_labels]
    ax.set_yticklabels(y_labels, fontsize=0.7*fontsize)

    # Adjust legend font properties and position
    plt.legend(bbox_to_anchor = (1.2, 0.3), loc='lower center', fontsize=0, prop={'family': fontname})
    ax.legend().set_visible(False)
    plt.grid(axis='y', linestyle='--', color='lightgray', zorder=-99)

    # Create plots directory if it doesn't exist
    os.makedirs('best_new_plots', exist_ok=True)
    
    # Save the DataFrame as CSV
    df.to_csv('best_new_plots/' + db_name + '-plot-data-' + relaxed + metric + '.csv', index=False)
    
    # Save the plot as a PDF file
    plt.savefig('best_new_plots/' + db_name + '-plot-' + relaxed + metric + '.pdf', format='pdf', bbox_inches='tight')

    plt.show()


def save_result_tables(path_to_dbs, db_name, relaxed):
    data = []
    parent_folder = path_to_dbs

    for folder in os.listdir(parent_folder):
        if folder.startswith(db_name):
            folder_path = os.path.join(parent_folder, folder, 'best_new_results')
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith('_METRICS.txt'):
                        parts = file.split('_')
                        prompt_name = parts[1] # Extract prompt name
                        file_path = os.path.join(folder_path, file)
                        try:
                            with open(file_path, 'r') as f:
                                file_content = f.read().strip()
                                if file_content and file_content != '{}':
                                    file_content = file_content.replace("'", '"')
                                    metrics = json.loads(file_content)
                                    # Only add if metrics contains valid data
                                    if metrics:
                                        data.append({
                                            'Database': folder,
                                            'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                            'Error': '',
                                            'Metrics': metrics
                                        })
                                    else:
                                        # Parsed but empty dict
                                        data.append({
                                            'Database': folder,
                                            'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                            'Error': 'NO_METRICS',
                                            'Metrics': {}
                                        })
                                else:
                                    # Empty or '{}'
                                    print(f"Warning: {file_path} is empty or contains empty dict.")
                                    data.append({
                                        'Database': folder,
                                        'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                        'Error': 'NO_METRICS',
                                        'Metrics': {}
                                    })
                            f.close()
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in file {file_path}: {e}")
                            data.append({
                                'Database': folder,
                                'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                'Error': 'JSON_DECODE_ERROR',
                                'Metrics': {}
                            })
                        except Exception as e:
                            print(f"Unexpected error processing file {file_path}: {e}")
                            data.append({
                                'Database': folder,
                                'Prompt': prompt_name.replace('prompt-','').replace('.txt',''),
                                'Error': f"ERROR:{type(e).__name__}",
                                'Metrics': {}
                            })

    df0 = pd.DataFrame(data)
    print(f"Found {len(data)} metric files (including errors) for {db_name}")
    
    # Always write an all-runs CSV, even if empty
    os.makedirs('best_new_plots', exist_ok=True)
    if df0.empty:
        # Write an empty CSV with headers
        pd.DataFrame(columns=['Database','Prompt','Error']).to_csv('best_new_plots/' + db_name + '-table-all_runs.csv', index=False)
        # Also write placeholder to new_plots
        os.makedirs('new_plots', exist_ok=True)
        pd.DataFrame(columns=['Database','Prompt','Error']).to_csv('new_plots/' + db_name + '-table.csv', index=False)
        print(f"No metric files found for {db_name}; wrote empty CSVs.")
        return

    # Put the Metrics column, which contains dicts, into a seperate dataframe
    dfm = pd.DataFrame.from_records(df0['Metrics'].values)
    # Combine the Metrics dataframe with the Folder+Prompt+Error columns from the original DataFrame
    df = pd.concat([df0[['Database','Prompt','Error']], dfm], axis=1)

    # Write the all-runs table
    df.to_csv('best_new_plots/' + db_name + '-table-all_runs.csv', index=False)

    # Calculate average metric values if multiple runs have occurred
    # Keep only numeric columns for aggregation
    numeric_cols = df.select_dtypes(include=[float, int]).columns.tolist()
    if numeric_cols:
        df_agg = df.groupby(['Database','Prompt'])[numeric_cols].mean()
        df_agg.reset_index(inplace=True)
        df_agg.set_index('Database')
        os.makedirs('new_plots', exist_ok=True)
        df_agg.to_csv('new_plots/' + db_name + '-table.csv', index=False)
    else:
        # No numeric metrics available; write a placeholder CSV with errors only
        os.makedirs('new_plots', exist_ok=True)
        df[['Database','Prompt','Error']].to_csv('new_plots/' + db_name + '-table.csv', index=False)

    return