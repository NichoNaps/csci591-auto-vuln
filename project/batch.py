import argparse
import csv
import sys

from test_chat_compl import LLM



# Remove excess spaces
def normalize_spaces(text: str) -> str:
    return ' '.join(text.split())


def check_output(output):
    if "VULNERABLE" in output:
        return 1
    elif "NOT VULNERABLE" in output:
        return 0
    else:
        print("***" + output + "***")


def run_batch(inputs_list, vulnerable_list):
    llm = LLM(verbose=False)

    for i, prompt in enumerate(inputs_list):

        llm.send('Please determine the intent of the following code:', role='system')

        # send the code
        llm.send(normalize_spaces(prompt))

        # let llm respond to the cod3
        llm.getResponse() 

        # prompt it to analyze
        llm.send("I want you to act as a vulnerability discovery system. Using your knowledge of the code given: "
                  "determine if the code has an exploitable vulnerability, and reply 'VULNERABLE' if the code is vulnerable, and 'NOT VULNERABLE' if the code is not vulnerable. DO NOT WRITE ANYTHING ELSE, just 'VULNERABLE' or 'NOT VULNERABLE'")

        resp = llm.getResponse() 


        # pretty print model history to make sure it is good
        llm.printHistory()


        if int(vulnerable_list[i]) == 1 and check_output(resp) == 1:
            print("THIS CODE IS VULNERABLE AND MODEL IS CORRECT")
        elif int(vulnerable_list[i]) == 0 and check_output(resp) == 0:
            print("THIS CODE IS NOT VULNERABLE AND MODEL IS CORRECT")
        else:
            print("MODEL IS INCORRECT")


        # reset llm history before starting the next one
        llm.clearHistory()


def input_list(filepath):
    # Set the max size for csv cells to max
    csv.field_size_limit(sys.maxsize)
    code_list = []
    vuln_list = []
    with open(filepath, mode='r') as file:
        i = -1
        csv_reader = csv.reader(file)
        for row in csv_reader:
            i += 1
            # This is to skip the header of the file
            if i == 0:
                continue
            # Grab code snippet and vulnerability flag and append them to list
            code = row[2]
            is_vuln = row[3]
            code_list.append(code)
            vuln_list.append(is_vuln)
            # This is just for testing purposes, change i's value to increase the number of samples run
            if i == 5:
                return code_list, vuln_list
    return code_list, vuln_list


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='batch',description='runs llm vuln tests')
    parser.add_argument('mode', choices=['cwe', 'vuln'], default='vuln', help='Specify whether to test vuln detection or CWE classification. Ex: "python3 batch.py cwe"')

    #@NOTE: we can use there to split up the running of things between different computers maybe
    # parser.add_argument('--start', type=int, help='where to start in the file')  
    # parser.add_argument('--end', type=int, help='where to end in the file')  
    args = parser.parse_args()



    # Perform vuln detection
    if args.mode == 'vuln':
        code_list, vuln_list = input_list("cleaned_train_data.csv")
        run_batch(code_list, vuln_list)
    
    # Perform CWE Classification
    elif args.mode == 'cwe':
        raise Exception("unimplemented!!")



