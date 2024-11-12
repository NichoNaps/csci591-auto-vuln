import subprocess


class Process:

    def __init__(self, cmd, shell=False):
        self.proc = subprocess.Popen(
            cmd,
            shell=shell,
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

    # TODO send outputs to files for analysis, make a method that checks correctness as it runs?
    def print_output(self):
        print("output")


def run_batch(inp_list):
    for prompt in inp_list:
        # start process
        proc = Process([f"python3 test_chat_compl.py"], shell=True)
        proc.send(prompt)
        # send command to break llama process loop
        proc.send("EXIT")
        # wait until process is completely finished
        proc.wait()
        # ensure process is fully closed before starting another one
        proc.terminate()
        print(proc.isAlive())



inp_list_test = ["Tell me a joke", "What is your purpose?", "repeat after me: FINAL"]
run_batch(inp_list_test)



