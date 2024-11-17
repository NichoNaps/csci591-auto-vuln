from util import *
import matplotlib.pyplot as plt
import copy
import numpy as np
import tkinter # fix plt

default_frequencies = {
    'true_pos': 0,
    'true_neg': 0,
    'false_pos': 0,
    'false_neg': 0,
    'invalid_response': 0,
}

variantResults = {
    'chain-of-thought': copy.deepcopy(default_frequencies),
    'in-context-learning': copy.deepcopy(default_frequencies),
}

for file in resultsPath.iterdir():
    if file.is_file() and file.stem.startswith('gpt-vuln'):
        with open(file, 'r') as f:
            data = json.load(f)
        
        dataset, variant, chunk = file.stem.split('_')

        # count the occurence of things in the json
        for res in data.values():
            variantResults[variant][res] += 1





labels = default_frequencies.keys()

x = np.arange(len(labels))  # the label locations
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for each variant
width = 0.3  
bars1 = ax.bar(x - width / 2, variantResults['chain-of-thought'].values(), width, label='Chain of Thought', color='blue')
bars2 = ax.bar(x + width / 2, variantResults['in-context-learning'].values(), width, label='In Context Learning', color='orange')

# Add labels, title, and legend
ax.set_xlabel("Response Type")
ax.set_ylabel("Count")
ax.set_title("Comparison of Response Types by Variant")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Show the plot
plt.tight_layout()
plt.show()