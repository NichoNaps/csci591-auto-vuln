import argparse
import csv
import sys
from pathlib import Path
import json
import hashlib
import math
import random

from test_chat_compl import LLM
from util import * 


def cwe_run_batch(tests, resultsFile, variant):
    llm = LLM(verbose=False)

    for idx, (cwes, code) in enumerate(tests):

        # if we've already tested this code, skip it
        if resultsFile.alreadyContains(code):
            continue

        print(f"\n############## Starting Test {idx + 1}/{len(tests)}")
        print(cwes, code)


        # adding cwe descriptions seems to help but we should still try full ICL stuff
        llm.send(f"You are a Vulnerability CWE classification system. You classify vulnerable code that is in the top 25 CWEs. Now list the top 25 CWEs and their descriptions:", role='system')
        llm.send(
            "The top 25 CWEs are:\n" + '\n'.join([f'{key} {value}' for key, value in top_25_cwes_desc.items()]),
            role='assistant')
        
        llm.send('As a Vulnerability CWE classification system you are also capable of understanding the semantics of code. Please determine the intent of the following code:', role='system')

        # send the code
        llm.send(code)

        # let llm respond to the code
        llm.getResponse() 

        llm.send(f"Using your knowledge about CWEs: "
                "determine the most likely CWE present in the code from the top 25 list and reply 'CWE-#' where # is replaced by the CWE number. DO NOT WRITE ANYTHING ELSE, just the cwe in that format.", role='system')



        # Start of the code for ICL if we want to do that:
        # with open(datasetsPath / 'diverse-vul/diVul_1.json') as f:
        #     data = json.load(f)
            

        #     for idx, row in enumerate(data):
        #         llm.send("The Code is: " +  normalize_spaces(row['func']) + " Let's start:", role='user')
        #         llm.send(row['cwe'][0], role='assistant') # @TODO this might not be a top 25 if multiple

        #         if idx > 5:
        #             break

        # llm.send("The Code is: " + code + " Let's start:")
        

        resp = llm.getResponse() 

        # pretty print model history to make sure it is good
        llm.printHistory()


        #@TODO how to interpret the response of the LLM???????
        # for cwe in top_25_cwes:
            #@TODO I think we use an all vs one thingy
            # raise Exception("Unimplemented")
            

        # reset llm history before starting the next one
        llm.clearHistory()




def vuln_check_output(output):
    if "code is non-vulnerable" in output:
        return 0
    elif "code is vulnerable" in output:
        return 1
    else:
        print("***" + output + "***")


def vuln_run_batch(tests, resultsFile: ResultsFile, variant='chain-of-thought'):
    llm = LLM(verbose=False)


    for idx, (is_vuln, prompt) in enumerate(tests):

        # if we've already tested this code, skip it
        if resultsFile.alreadyContains(prompt):
            # print("Skipped, already computed.")
            continue

        print(f"\n############## Starting Test {idx + 1}/{len(tests)}")


        if variant == 'chain-of-thought':
        
            llm.send('Please determine the intent of the following code:', role='system')

            # send the code
            llm.send(prompt)

            # let llm respond to the cod3
            llm.getResponse() 

            # prompt it to analyze
            llm.send("Now you need to identify whether this code contains a potential vulnerability or not. If it has any potential vulnerability, output: 'this code is vulnerable'. Otherwise, output: 'this code is non-vulnerable'. You only need to give the prior two answers. Let's Start: ")


        elif variant == 'in-context-learning':
            llm.send("You are a vulnerability discovery system. Using your knowledge of the code given: "
                    "determine if the code has an exploitable vulnerability, and reply 'this code is vulnerable' if the code is vulnerable, and 'this code is non-vulnerable' if the code is not vulnerable. DO NOT WRITE ANYTHING ELSE, just 'this code is vulnerable' or 'this code is non-vulnerable'", role='system')

            with open(datasetsPath / 'gpt-vuln/cleaned_train_data.csv') as f:
                csv_reader = csv.reader(f)

                # skip the header
                next(csv_reader) 

                for idx, row in enumerate(csv_reader):
                    llm.send("The Code is: " +  normalize_spaces(row[2]) + " Let's start:", role='user')
                    llm.send('this code is vulnerable.' if int(row[3]) == 1 else 'this code is non-vulnerable.', role='assistant')

                    # it crashes my desktop if we set this to 10
                    if idx > 7:
                        break

            llm.send("The Code is: " + prompt + "\n Let's Start: ", role='system')
        
        else:
            raise Exception(f"Unknown variant {variant}")
            

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
    parser.add_argument('chunk', type=int, choices=[1,2,3,4], help='which chunk of the tests to run')  

    parser.add_argument('--variant', type=str, default=None, help='optionally specify an extra flag')  

    args = parser.parse_args()



    # Perform vuln detection
    if args.mode == 'vuln':

        # set a default variant mode
        if args.variant is None:
            args.variant = 'chain-of-thought'

        # Pre-process and get tests
        tests = vuln_parse_input_list(datasetsPath / "gpt-vuln/Cleaned_test_for_codexglue_binary.csv")
        print(f"Total Tests: {len(tests)}")

        # split tests into 4 chunks (the last chunk might be slightly smaller)
        tests = list(chunks(tests, math.ceil(len(tests)/4)))[args.chunk -1]
        print(f"Using Chunk {args.chunk} with size {len(tests)}")

        # save this chunk into a dedicated file
        resultsFile = ResultsFile(f'gpt-vuln_{args.variant}_chunk{args.chunk}') 
        vuln_run_batch(tests, resultsFile, variant=args.variant)
    
    # Perform CWE Classification
    elif args.mode == 'cwe':

        # set a default variant mode
        if args.variant is None:
            args.variant = 'TODO-Something'


        with open(datasetsPath / f"diverse-vul/reduced_cwe_dataset.json", 'r') as f:
            tests = json.load(f)

        print(f"Total Tests: {len(tests)}")

        # split tests into 4 chunks (the last chunk might be slightly smaller)
        tests = list(chunks(tests, math.ceil(len(tests)/4)))[args.chunk -1]
        
        # grab just the fields we need
        tests = [(row['cwe'], normalize_spaces(row['func'])) for row in tests]

        print(f"Using Chunk {args.chunk} with size {len(tests)}")
        resultsFile = ResultsFile(f'diverse-vul_{args.variant}_chunk{args.chunk}') 


        cwe_run_batch(tests, resultsFile, args.variant)




