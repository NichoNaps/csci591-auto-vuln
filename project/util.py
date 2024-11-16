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

