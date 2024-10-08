import subprocess
import time
import hashlib
from pathlib import Path
import datetime
import json
from concurrent.futures import ProcessPoolExecutor, wait


# wrapper around pythons process type to add 
# some simplified methods for our use case
class ProcWrap:

    def __init__(self, cmd, shell=False):
        self.proc = subprocess.Popen(
            cmd,
            shell = shell,
            stdin = subprocess.PIPE,
            universal_newlines = True,
            bufsize = 0,
        )


    def isAlive(self):
        return self.proc.poll() == None

    
    # send a string to the process. Returns success bool.
    def send(self, data: str, postfix="\n") -> bool: 
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


def fileToString(path):
    # occasionally there will be non-utf8 characters so replace those with '?'
    with open(path, 'r',  encoding="utf-8", errors='replace') as f:
        return f.read()

# yield list in chunks (https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks)
def chunks(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


class Harness:

    def __init__(self) -> None:
        self.logPath = Path(__file__).parent / 'logs'
        self.crashesPath = self.logPath / 'crashes'
        self.tempPath = self.logPath / 'temp'

        # ensure folders exist
        self.logPath.mkdir(exist_ok=True)
        self.crashesPath.mkdir(exist_ok=True)
        self.tempPath.mkdir(exist_ok=True)


        self.resultsFilePath = self.logPath / 'results.json'

        # try loading the crash file containing the run hashes
        if self.resultsFilePath.exists():
            with open(self.resultsFilePath, 'r') as f:
                self.results = json.load(f)
        else:
            self.results = {}
    
    # save the file containing the results of each hash
    def saveResults(self):
        with open(self.resultsFilePath, 'w') as f:
            json.dump(self.results, f)
    
    # delete all temp files
    def nukeTempFolder(self):
        for item in self.tempPath.iterdir():
            if item.is_file():
                item.unlink()

    # gen unique hash of inputs
    def hashInputs(self, inputs):
        inputsHash = hashlib.sha256(str(inputs).encode('utf-8')).hexdigest()[:15]
        return inputsHash


    # run a single test
    def run(self, inputs, port=2525, silent=False):
        print('port', port)

        # create a unique crash path filename based on the inputs
        inputsHash = self.hashInputs(inputs)
        crashPath = self.crashesPath / f'{inputsHash}.json'
        
        if inputsHash in self.results.keys():
            print('inputs already tried')
            return inputsHash, 'dup'

        # create unique temp files
        serverLogPath = self.tempPath / f'temp_server_{port}.log'
        telnetLogPath = self.tempPath / f'temp_telnet_{port}.log'

        silentString = '> /dev/null' if silent else ''

        procServer = ProcWrap([f"script -c './voidsmtpd {port}' {serverLogPath} {silentString}"], shell=True)
        time.sleep(0.2)
        if not procServer.isAlive():
            print("Unexpected Error voidserver:")
            print(fileToString(serverLogPath))

        procTelnet = ProcWrap([f"script -c 'telnet localhost {port}' {telnetLogPath} {silentString}"], shell=True)
        time.sleep(0.2)
        if not procTelnet.isAlive():
            print("Unexpected Error in telnet:")
            print(fileToString(telnetLogPath))


        for idx, userInput in enumerate(inputs):

            # if something died we crashed
            if not procServer.isAlive() or not procTelnet.isAlive():
                break
            
            # send user input to telnet
            procTelnet.send(userInput)

            time.sleep(0.2)

        procServer.terminate()
        procTelnet.terminate()

        serverLogs = fileToString(serverLogPath)
        telnetLogs = fileToString(telnetLogPath)

        # sometimes the server will just kick the telnet process so 
        # its not an actual crash so don't count this as a crash
        # unless it has address sanitizer in it
        crashed = "AddressSanitizer" in serverLogs

        # if we've crashed save a crash report
        if crashed:

            report = {
                        "datetime": str(datetime.datetime.now()),
                        "inputs": inputs,
                        "outputs": {
                            "server": [line for line in serverLogs.split('\n') if line != ''],
                            "telnet": [line for line in telnetLogs.split('\n') if line != ''],
                        }
                      }

            with open(crashPath, 'w') as f:
                json.dump(report, f, indent=4)
        

            return inputsHash, 'crash'
        

        # there should always be a BYE at the end if it rand correctly
        if "221 Bye" in telnetLogs:
            return inputsHash, 'ran'


        # something about the test seems to have gone wrong, report that the test failed
        return inputsHash, '?'


    def runBatch(self, manyInputs, silent=False, startPort=4000):

        with ProcessPoolExecutor() as exe:
            
            # run up to 3,000 consecutively. This is to avoid port collisions. could up it more if needed
            for chunk in chunks(manyInputs, 3000):

                # clean out junk
                self.nukeTempFolder()

                ProcWrap(["pkill voidsmtpd"], shell=True)


                jobs = [exe.submit(self.run, aInput, startPort + idx, silent) for idx, aInput in enumerate(chunk)]

                # let these finish so the ports are free
                wait(jobs)

                # update the results to keep track of what input hashes we have run
                print("Input Verdicts:")
                for job in jobs:
                    inputHash, verdict = job.result()

                    print(f"{inputHash} -> {('ran' if self.results[inputHash] else 'crash') if verdict == 'dup' else verdict}")

                    if verdict == 'ran':
                        self.results[inputHash] = True

                    elif verdict == 'crash':
                        self.results[inputHash] = False
                
                self.saveResults()


if __name__=="__main__":
    harness = Harness()

    for report in harness.crashesPath.iterdir():
        with open(report, 'r') as f:
            data = json.load(f)


        serverLogs = '\n'.join(data['outputs']['server'])

        if "in print_list" not in serverLogs or "SEGV on unknown address" not in serverLogs:
            print(report)


        # print(data)

    # harness.run(
    #     [
    #     "HELO 8HDf84QvDM",
    #     "MAIL FROM:<qdCd@Hv0zS.com>",
    #     "RCPT TO:<jDLX@hq.com>",
    #     "DATA",
    #     "To: asdfl3asdfa\" <jDLX@hq.com>",
    #     "From: \"Potato\" <qdCd@Hv0zS.com>",
    #     "From: \"Potato\" <qdCd@Hv0zS.com>",
    #     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    #     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    #     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    #     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    #     "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    #     ".",
    #     "QUIT"
    #     ]
            
    #     , silent=False, port=2000)
