import argparse
import csv
import sys
from pathlib import Path
import json
import hashlib
import math

from test_chat_compl import LLM
from util import * 


def cwe_run_batch(tests, resultsFile):
    llm = LLM(verbose=False)

    for idx, (cwes, code) in enumerate(tests):
        print(cwes, code)

        raise Exception("unimplemented!!")




def vuln_check_output(output):
    if "VULNERABLE" in output:
        return 1
    elif "NOT VULNERABLE" in output:
        return 0
    else:
        print("***" + output + "***")


def vuln_run_batch(tests, resultsFile: ResultsFile):
    llm = LLM(verbose=False)


    for idx, (is_vuln, prompt) in enumerate(tests):

        # if we've already tested this code, skip it
        if resultsFile.alreadyContains(prompt):
            # print("Skipped, already computed.")
            continue

        print(f"\n############## Starting Test {idx + 1}/{len(tests)}")


        llm.send('Please determine the intent of the following code:', role='system')

        # send the code
        llm.send(prompt)

        # let llm respond to the cod3
        llm.getResponse() 

        # prompt it to analyze
        llm.send("I want you to act as a vulnerability discovery system. Using your knowledge of the code given: "
                  "determine if the code has an exploitable vulnerability, and reply 'VULNERABLE' if the code is vulnerable, and 'NOT VULNERABLE' if the code is not vulnerable. DO NOT WRITE ANYTHING ELSE, just 'VULNERABLE' or 'NOT VULNERABLE'")

        resp = llm.getResponse() 


        # pretty print model history to make sure it is good
        llm.printHistory()


        if is_vuln == 1 and vuln_check_output(resp) == 1:
            print("THIS CODE IS VULNERABLE AND MODEL IS CORRECT")
            resultsFile.add(prompt, 'true_pos')
        elif is_vuln == 0 and vuln_check_output(resp) == 0:
            print("THIS CODE IS NOT VULNERABLE AND MODEL IS CORRECT")
            resultsFile.add(prompt, 'true_neg')
        else:
            if is_vuln == 1 and vuln_check_output(resp) == 0:
                print("FALSE NEGATIVE")
                resultsFile.add(prompt, 'false_neg')
            elif is_vuln == 0 and vuln_check_output(resp) == 1:
                print("FALSE POSITIVE")
                resultsFile.add(prompt, 'false_pos')

            # If the model gave an invalid response save that it errored out
            else:
                resultsFile.add(prompt, 'invalid_response')

        # reset llm history before starting the next one
        llm.clearHistory()
    


def vuln_parse_input_list(filepath):

    # Set the max size for csv cells to max
    csv.field_size_limit(sys.maxsize)
    tests = []
    
    with open(filepath, mode='r') as file:

        csv_reader = csv.reader(file)

        # skip the header
        next(csv_reader) 

        for row in csv_reader:

            # Grab code snippet and vulnerability flag and append them to list
            tests.append((int(row[2]), normalize_spaces(row[3])))

    # take only your part
    return tests 


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='batch',description='runs llm vuln tests')
    parser.add_argument('mode', choices=['cwe', 'vuln'], default='vuln', help='Specify whether to test vuln detection or CWE classification. Ex: "python3 batch.py cwe 2"')
    parser.add_argument('chunk', type=int, choices=[1,2,3,4], help='which chunk of the test to run')  

    args = parser.parse_args()



    # Perform vuln detection
    if args.mode == 'vuln':

        # Pre-process and get tests
        tests = vuln_parse_input_list(datasetsPath / "gpt-vuln/Cleaned_test_for_codexglue_binary.csv")
        print(f"Total Tests: {len(tests)}")

        # split tests into 4 chunks (the last chunk might be slightly smaller)
        tests = list(chunks(tests, math.ceil(len(tests)/4)))[args.chunk -1]
        print(f"Using Chunk {args.chunk} with size {len(tests)}")

        # save this chunk into a dedicated file
        resultsFile = ResultsFile(f'gpt-vuln-chunk{args.chunk}') 
        vuln_run_batch(tests, resultsFile)
    
    # Perform CWE Classification
    elif args.mode == 'cwe':

        with open(datasetsPath / f"diverse-vul/diVul_{args.chunk+1}.json", 'r') as f:
            tests = json.load(f)
        
        # grab just the fields we need
        tests = [(row['cwe'], normalize_spaces(row['func'])) for row in tests]

        print(f"Using Chunk {args.chunk} with size {len(tests)}")
        resultsFile = ResultsFile(f'diverse-vul-chunk{args.chunk}') 


        cwe_run_batch(tests, resultsFile)




