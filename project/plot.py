from util import *
import matplotlib.pyplot as plt

import tkinter # fix plt

frequencies = {
    'true_pos': 0,
    'true_neg': 0,
    'false_pos': 0,
    'false_neg': 0,
    'invalid_response': 0,
}
for file in resultsPath.iterdir():
    if file.is_file():
        with open(file, 'r') as f:
            data = json.load(f)

        # count the occurence of things in the json
        for res in data.values():
            frequencies[res] += 1

# Generate a bar chart
plt.figure(figsize=(10, 6))
plt.bar(frequencies.keys(), frequencies.values(), color=['red', 'blue', 'green', 'orange', 'purple'])
plt.xlabel("Response Type")
plt.ylabel("Count")
plt.title("Counts Result Types")
plt.show()
