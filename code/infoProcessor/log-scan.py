import re
import sys
import os
import json
import argparse

def is_word_in_exclude_list(match_string, exclude_list):
    in_list = False
    for i in exclude_list:
        if (i.strip() in match_string):
            print('\nExclusion: ' + i.strip() + ' is in matched string.')
            in_list = True

    return in_list

def logscan (path_to_log, path_to_exclusions=None):
    print('\n---Starting Log Scan!---\n')

    findings = []

    # load exclusions
    if (path_to_exclusions != None):
        exclusion_file = open(path_to_exclusions)
        exclude_list = exclusion_file.readlines()
        print('\nLoading exclusions list')
        print(exclude_list)
    else:
        exclude_list = []

    # open file with regex patterns
    regex_file = open('patterns.txt')
    regex_lines = regex_file.readlines()

    f = open(path_to_log, 'r')
    text = f.read()
    
    # iterate through logs line by line
    for ln in regex_lines:
        regex_pattern = re.compile(ln)
        for i, line in enumerate(open(path_to_log)):
            for match in re.finditer(regex_pattern, line):
                if (not is_word_in_exclude_list(match.group(), exclude_list)):
                    print ('Found on line ' + str(i+1) + ':' + match.group())
                    findings.append({"pattern": ln, "match": match.group(), "line number": str(i+1), "line": line })


    # create result json file with all the findings and metadata
    log_data = {
        "file": path_to_log,
        "findings": findings
    }

    # will have same name as the log file but .json extension
    result_json = path_to_log.split('/')[-1] + '.json'

    result_json_path = os.path.join(os.getcwd(), 'results', result_json)
    if not os.path.exists('results'):
        os.makedirs('results')
    
    
    if (findings != []):
        print('\nFindings:\n')
        print(json.dumps(log_data, indent=4))
    
        with open(result_json_path, "w") as result_file:
            json.dump(log_data, result_file)
    else:
        print('\nNo Sensitive data found\n')

    print('\n---Scan is over---\n')
    
    return log_data

if (__name__ == '__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', required=True, help='Specify path to the log')
    parser.add_argument('-e', '--exclusions', required=False, help='Specify path to exclusions file')
    args = parser.parse_args()

    path_to_log = args.log
    path_to_exclusions = args.exclusions

    logscan(path_to_log, path_to_exclusions)

