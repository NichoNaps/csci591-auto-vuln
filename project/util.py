from pathlib import Path
import json
import hashlib


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
            json.dump(self.results, f)# indent=2)


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



# Top 25 CWE list from Mitre 2021
top_25_cwes = {
    "CWE-787", "CWE-79", "CWE-125", "CWE-20", "CWE-78", "CWE-89", "CWE-416",
    "CWE-22", "CWE-352", "CWE-434", "CWE-306", "CWE-190", "CWE-502", "CWE-287",
    "CWE-476", "CWE-798", "CWE-119", "CWE-862", "CWE-276", "CWE-200", "CWE-522",
    "CWE-732", "CWE-611", "CWE-918", "CWE-77"
}
top_25_cwes_desc = {
    "CWE-787":  "Out-of-bounds Write",
    "CWE-79": "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
    "CWE-125":  "Out-of-bounds Read",
    "CWE-20": "Improper Input Validation",
    "CWE-78": "Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
    "CWE-89": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
    "CWE-416":  "Use After Free",
    "CWE-22": "Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
    "CWE-352":  "Cross-Site Request Forgery (CSRF)",
    "CWE-434":  "Unrestricted Upload of File with Dangerous Type",
    "CWE-306":  "Missing Authentication for Critical Function",
    "CWE-190":  "Integer Overflow or Wraparound",
    "CWE-502":  "Deserialization of Untrusted Data",
    "CWE-287":  "Improper Authentication",
    "CWE-476":  "NULL Pointer Dereference",
    "CWE-798":  "Use of Hard-coded Credentials",
    "CWE-119":  "Improper Restriction of Operations within the Bounds of a Memory Buffer",
    "CWE-862":  "Missing Authorization",
    "CWE-276":  "Incorrect Default Permissions",
    "CWE-200":  "Exposure of Sensitive Information to an Unauthorized Actor",
    "CWE-522":  "Insufficiently Protected Credentials",
    "CWE-732":  "Incorrect Permission Assignment for Critical Resource",
    "CWE-611":  "Improper Restriction of XML External Entity Reference",
    "CWE-918":  "Server-Side Request Forgery (SSRF)",
    "CWE-77": "Improper Neutralization of Special Elements used in a Command ('Command Injection')",
}



def getDefaultFrequencies(): 
    return {
        'true_pos': 0,
        'true_neg': 0,
        'false_pos': 0,
        'false_neg': 0,
        'invalid_response': 0,
    }

def mergeFrequencies(*freqs):
    res = freqs[0]
    for freq in freqs[1:]:
        for key in res.keys():
            res[key] += freq[key]
    
    return res

