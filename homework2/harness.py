import subprocess
import time
import threading 
import queue
from pathlib import Path
from multiprocessing import Pool

# consume a blocking call that returns strings into a single concatted string
# in a non-blocking way
class BlockingConsumer:
    def __init__(self, call):
        self.queue = queue.Queue()
        self.call = call

        self.thread = threading.Thread(target=self._readThreadWorker)
        self.thread.start()


    def _readThreadWorker(self):
        print("Started consume thread")

        while True:
            # this is a blocking call

            char = self.call()
            # print("Found char! ", char)

            # load it into the thread safe queue
            self.queue.put(char)

    # returns a string of the output if there is any
    # if there is nothing to return then return None
    def get(self) -> str | None:

        output = ""

        # consume the queue items
        while not self.queue.empty():
            output += self.queue.get()
            self.queue.task_done()


        if output == "":
            return None

        return output


# wrapper around pythons process type to add 
# some simplified methods for our use case
class ProcWrap:

    def __init__(self, cmd, shell=False):
        self.proc = subprocess.Popen(
            cmd,
            shell = shell,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True,
            bufsize = 0,
        )


        # immediately test if the process failed to start and panic about it
        time.sleep(0.3)
        if not self.isAlive():
            stdout, stderr = self.proc.communicate()

            print(f"stdout:{stdout}, stderr:{stderr}")
            exit()

        # startup consumers for output
        self.stdout = BlockingConsumer(lambda: self.proc.stdout.read(1))

        # we are using script command so stdout and stderr get combined into stdout
        # self.stderr = BlockingConsumer(lambda: self.proc.stderr.read(1))

    def isAlive(self):
        return self.proc.poll() == None
    
    def send(self, data: str, postfix="\n") -> bool: 
        try:
            self.proc.stdin.write(data + postfix)

            # make sure to send command
            self.proc.stdin.flush()  

            return True

        except Exception as e:
            print("unable to send input")
            return False
    

    def read(self):
        return self.stdout.get()
    
    def terminate(self):
        self.proc.terminate()


def repl():
    port = 8889
    procServer = ProcWrap([f"script -c './voidsmtpd {port}' temp.txt && tail -f -n +1 temp.txt"], shell=True)
    procTelnet = ProcWrap([f"script -c 'telnet localhost {port}'"], shell=True)

    while True:

        # if there was output print it
        if output := procServer.read():
            for line in output.strip().split('\n'):
                print(f"[VoidServer Process]: {line}") 

        # if there was output print it
        if output := procTelnet.read():
            for line in output.strip().split('\n'):
                print(f"[Telnet Process]: {line}")

        # send user input to telnet
        print()
        procTelnet.send(input("Enter something to send to telnet > ").strip())

        time.sleep(0.2)


class Harness:

    def __init__(self) -> None:
        self.path = Path('./logs')
        self.path.mkdir(exist_ok=True)

    def run(self, inputGenerator, port=2525):
        inputs = inputGenerator() # returns a list of strings

        procServer = ProcWrap([f"script -c './voidsmtpd {port}' temp.txt && tail -f -n +1 temp.txt"], shell=True)
        procTelnet = ProcWrap([f"script -c 'telnet localhost {port}'"], shell=True)

        log = []
        crashed = False

        for idx, userInput in enumerate(inputs):

            # if something died we crashed
            if not procServer.isAlive() or not procTelnet.isAlive():
                crashed = True
                break
            
            # send user input to telnet
            procTelnet.send(userInput)

            log.append(f"[User Input]: {userInput.strip()}")

            time.sleep(0.2)

            # if there was output print it
            if output := procServer.read():
                for line in output.strip().split('\n'):
                    log.append(f"[VoidServer Process]: {line}") 

            # if there was output print it
            if output := procTelnet.read():
                for line in output.strip().split('\n'):
                    log.append(f"[Telnet Process]: {line}")


        # if there was output print it
        if output := procServer.read():
            for line in output.strip().split('\n'):
                log.append(f"[VoidServer Process]: {line}") 

        # if there was output print it
        if output := procTelnet.read():
            for line in output.strip().split('\n'):
                log.append(f"[Telnet Process]: {line}")

        print(log)
        stdout, stderr = procServer.proc.communicate()
        print(stdout)

        procServer.terminate()
        procTelnet.terminate()

    
        if crashed:
            return log
        else:
            return None
            


if __name__=="__main__":
    # repl()
    harness = Harness()

    #@TODO this causes a crash but the crash has a non-utf8 character which crashes the consumer
    log = harness.run(lambda: [
        "HELO csci591",
        "MAIL FROM:<c@9aw384htjeaotapw4t09jeac.asdfacom>",
        "RCPT TO:<e@e.com>",
        "DATA",
        """From c\nTo: d, e\nHjklf""",
        ".",
        "QUIT"])

    
    if log is not None:
        print(f"\n\ncash detected in logs:")
        for row in log:
            print(row.strip())
    else:
        print("no crash")

#@TODO the mail server sometimes just kicks you for passing the wrong thing, tell this apart from crashes
#@TODO log inputs and outputs for crashes
#@TODO parallelize 