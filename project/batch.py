import subprocess
import csv
import sys


class Process:

    def __init__(self, cmd, shell=False):
        self.proc = subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            bufsize=0,
        )

    def isAlive(self):
        return self.proc.poll() == None

    # Wait method to ensure process is completed before starting another one
    def wait(self):
        self.proc.wait()

    # send a string to the process. Returns success bool.
    def send(self, data: str, postfix="\nSEND\n") -> bool:
        try:
            self.proc.stdin.write(data + postfix)

            # make sure to send command
            self.proc.stdin.flush()

            return True

        except Exception as e:
            print("unable to send input")
            return False

    def terminate(self):
        self.proc.terminate()

    def get_output(self):
        stdout, stderr = self.proc.communicate()
        lines = stdout.splitlines()
        return lines
        # for line in lines:
        #     print(line)
        #     print("Lines!")
        # while True:  # Read line by line from stdout
        #     output = self.proc.stdout.readline()
        #     if output == '' and self.proc.poll() is not None:
        #         break
        #     if output:
        #         print(output.strip())
        #         print("Lines!")


    # TODO send outputs to files for analysis, make a method that checks correctness as it runs?
    def print_output(self):
        print("output")


def check_output(output_list):
    for line in output_list:
        if "AI: VULNERABLE" in line:
            return 1
        elif "AI: NOT VULNERABLE" in line:
            return 0
        else:
            print("***" + line + "***")


def run_batch(inputs_list, vulnerable_list):
    i = 0
    for prompt in inputs_list:
        # start process
        proc = Process([f"python3 test_chat_compl.py"], shell=True)
        # proc.get_output()
        # send the code
        proc.send(prompt)
        # prompt it to analyze
        proc.send("I want you to act as a vulnerability discovery system. Using your knowledge of the code given: "
                  "determine if the code has an exploitable vulnerability, and reply 'VULNERABLE' if the code is vulnerable, and 'NOT VULNERABLE' if the code is not vulnerable. DO NOT WRITE ANYTHING ELSE, just 'VULNERABLE' or 'NOT VULNERABLE'")
        # send command to break llama process loop
        proc.send("EXIT")
        # wait until process is completely finished
        proc.wait()
        if int(vulnerable_list[i]) == 1 and check_output(proc.get_output()) == 1:
            print("THIS CODE IS VULNERABLE AND MODEL IS CORRECT")
        elif int(vulnerable_list[i]) == 0 and check_output(proc.get_output()) == 0:
            print("THIS CODE IS NOT VULNERABLE AND MODEL IS CORRECT")
        else:
            print("MODEL IS INCORRECT")
        # ensure process is fully closed before starting another one
        proc.terminate()
        i += 1


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


code_list, vuln_list = input_list("cleaned_train_data.csv")
run_batch(code_list, vuln_list)

