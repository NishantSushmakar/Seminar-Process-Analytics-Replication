import os
import csv
import re

def save_string_to_csv(filename, string_to_save):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([string_to_save])

def create_unique_file(file_path):
    directory, file_name = os.path.split(file_path)
    name, ext = os.path.splitext(file_name)
    index = 1
    new_file_name = f"{index:03d}_{name}{ext}"
    new_file_path = os.path.join(directory, new_file_name)
    while os.path.exists(new_file_path):
        index += 1
        new_file_name = f"{index:03d}_{name}{ext}"
        new_file_path = os.path.join(directory, new_file_name)
    return new_file_path


def save_results(chain_response:dict, output_dir:str, prompt_file:str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # save PROMPT
    file_name = prompt_file + '_PROMPT.txt'
    file_path = os.path.join(output_dir, file_name)
    #if os.path.isfile(file_path): file_path = create_unique_file(file_path)
    file_path = create_unique_file(file_path)
    with open(file_path, "w") as file:
        file.write(chain_response['messages'][0])
    
    # save executed SQL statement
    file_name = prompt_file + '_SQL.txt'
    file_path = os.path.join(output_dir, file_name)
    #if os.path.isfile(file_path): file_path = create_unique_file(file_path)
    file_path = create_unique_file(file_path)
    with open(file_path, "w") as file:
        file.write(chain_response['agent_response'])
    
    # save EVENTLOG
    file_name = prompt_file + '_EVENTLOG.csv'
    file_path = os.path.join(output_dir, file_name)
    #if os.path.isfile(file_path): file_path = create_unique_file(file_path)
    file_path = create_unique_file(file_path)
    save_string_to_csv(file_path, chain_response['sqlexecuter']) if isinstance(chain_response['sqlexecuter'], str) else chain_response['sqlexecuter'].to_csv(file_path, index=False)

    # save RESULTS
    file_name = prompt_file + '_METRICS.txt'
    file_path = os.path.join(output_dir, file_name)
    #if os.path.isfile(file_path): file_path = create_unique_file(file_path)
    file_path = create_unique_file(file_path)
    with open(file_path, "w") as file:
        file.write(str(chain_response['result']))

def extract_sql_statement(text):
    sql_pattern = re.compile(r"(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE|TRUNCATE|MERGE|CALL|EXPLAIN|SHOW|USE|IS|NOT|AND|NULL|UNION|ALL|WHERE|FROM)\b.*?;", re.IGNORECASE | re.DOTALL)
    match = sql_pattern.search(text)
    # If a match is found, return the matched string
    if match:
        return match.group(0)
    else:
        return text #"no sql query in agent response."        