import subprocess
import time
import threading 
import queue


# consume a blocking call that returns strings into a single concatted string
# in a non-blocking way
class Consumer:
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


        # immediately test if the process failed
        time.sleep(0.3)
        if self.proc.poll() != None:
            stdout, stderr = self.proc.communicate()

            print(f"stdout:{stdout}, stderr:{stderr}")
            exit()

        # startup consumers for output
        self.stdout = Consumer(lambda: self.proc.stdout.read(1))
        self.stderr = Consumer(lambda: self.proc.stderr.read(1))

    
    def send(self, data: str, postfix="\n"): 
        self.proc.stdin.write(data + postfix)

        # make sure to send command
        self.proc.stdin.flush()  
    

    def read(self):
        return self.stdout.get()
    
    def terminate(self):
        self.proc.terminate()




port = 8889
procServer = ProcWrap([f"script -c './voidsmtpd {port}' temp.txt && tail -f -n +1 temp.txt"], shell=True)
procTelnet = ProcWrap(["telnet", "localhost", str(port)])


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
    procTelnet.send(input("Enter something to send to telnet > "))


    time.sleep(0.2)


#@TODO do something about combining stdout and stderr instead of only reading stdout? maybe script should be used everywhere?
#@TODO log inputs and outputs 
#@TODO parallelize 