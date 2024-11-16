import argparse
import csv
import sys
from pathlib import Path
import json
import hashlib
import math

from test_chat_compl import LLM

# Define folder paths
rootPath = Path(__file__).parent.resolve()
resultsPath = rootPath / 'results'
datasetsPath = rootPath / 'datasets'

# create folders if they don't exist
resultsPath.mkdir(exist_ok=True)
datasetsPath.mkdir(exist_ok=True)



# Save and load a results file so you can add new results and skip
# already computed results.
class ResultsFile:

    def __init__(self, name):
        self.path = resultsPath / f"{name}.json"

        # if we have existing data load it
        if self.path.exists():
            with open(self.path, 'r') as f:
                self.results = json.load(f)
        else:
            self.results = {} # create a new empty 
    

    # Check if we have already run this test
    def alreadyContains(self, text: str):
        
        if hashData(text) in self.results.keys():
            return True
        
        return False

    
    # Add a test to this results file
    def add(self, text: str, res):

        dataHash = hashData(text)

        self.results[dataHash] = res

        # write to disk
        self.save()

    
    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.results, f)


# yield list in chunks (https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks)
def chunks(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]

# Remove excess spaces from a string
def normalize_spaces(text: str) -> str:
    return ' '.join(text.split())

# gen unique hash of string data
def hashData(data: str):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()[:15]


def vuln_check_output(output):
    if "VULNERABLE" in output:
        return 1
    elif "NOT VULNERABLE" in output:
        return 0
    else:
        print("***" + output + "***")


def vuln_run_batch(tests, resultsFile: ResultsFile):
    llm = LLM(verbose=False)


    for is_vuln, prompt in tests:

        # if we've already tested this code, skip it
        if resultsFile.alreadyContains(prompt):
            print("Skipped, already computed.")
            continue

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
        raise Exception("unimplemented!!")



