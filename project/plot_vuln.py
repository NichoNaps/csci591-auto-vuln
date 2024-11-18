from util import *
import matplotlib.pyplot as plt
import copy
import numpy as np
import tkinter # fix plt

# This file computes stats and plots vulnerability detection


variantResults = {}

for file in resultsPath.iterdir():
    if file.is_file() and file.stem.startswith('gpt-vuln'):
        with open(file, 'r') as f:
            data = json.load(f)
        
        dataset, variant, chunk = file.stem.split('_')

        # count the occurrence of things in the json
        for res in data.values():

            # if new variant then initialize it 
            if variant not in variantResults:
                variantResults[variant] = getDefaultFrequencies()

            variantResults[variant][res] += 1




for idx, (variant, freqs) in enumerate(variantResults.items()):

    # https://machinelearningmastery.com/precision-recall-and-f-measure-for-imbalanced-classification/

    #@TODO what do we do with invalid_response?

    # higher is better for all of these
    recall = freqs['true_pos'] / (freqs['true_pos'] + freqs['false_neg'])
    precision = freqs['true_pos'] / (freqs['true_pos'] + freqs['false_pos'])
    F1 = 2 * (precision * recall) / (precision + recall) # f1 represents a combination of both precision and recall

    # print stats
    print()
    print(variant)
    print(f"Recall: {recall}")
    print(f"Precision: {precision}")
    print(f"F1: {F1}")



labels = getDefaultFrequencies().keys()

x = np.arange(len(labels))  # the label locations
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars for each variant
width = 0.7 / len(variantResults)
for idx, (variant, freqs) in enumerate(variantResults.items()):
    bars1 = ax.bar(x - (width * len(variantResults))/2 + width/2 + width * idx, freqs.values(), width, label=variant)

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