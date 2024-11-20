from util import *
import matplotlib.pyplot as plt
import copy
import numpy as np
import json
import tkinter # fix plt

# This file computes stats and plots vulnerability detection


"""
1. We can compute the f1 score/precision for just each class
2. Compute the micro average to look at the overall performance. We use micro average because the dataset is imbalanced (has no CWE-306 for example)
"""


variantResults = {}

default_variant = {
    'individual': {cwe:getDefaultFrequencies() for cwe in top_25_cwes}, # sum of freqs for each individual class
    'aggregate': getDefaultFrequencies(), # sum of freqs over all classes
}

for file in resultsPath.iterdir():
    if file.is_file() and file.stem.startswith('diverse-vul'):
        with open(file, 'r') as f:
            data = json.load(f)
        
        dataset, variant, chunk = file.stem.split('_')

        # if new variant then initialize it 
        if variant not in variantResults:
            variantResults[variant] = copy.deepcopy(default_variant)

        for row in data.values():

            # count the occurrence of things in the json
            for cwe, freq in row.items():
                
                # turn freqs back into a dictionary
                freq = {key:value for key, value in zip(getDefaultFrequencies().keys(), freq)} 

                # sum individual class results
                mergeFrequencies(variantResults[variant]['individual'][cwe], freq)

                # sum aggregate results
                mergeFrequencies(variantResults[variant]['aggregate'], freq)


def computeStats(freq: dict):
    try:

        # higher is better for all of these
        recall = freq['true_pos'] / (freq['true_pos'] + freq['false_neg'])
        precision = freq['true_pos'] / (freq['true_pos'] + freq['false_pos'])
        f1 = 2 * (precision * recall) / (precision + recall) # f1 represents a combination of both precision and recall

        accuracy = (freq['true_pos'] + freq['true_neg']) / sum(freq.values())


        return accuracy, recall, precision, f1
        
    except Exception as e:
        # print(e)

        return None, None, None, None


for idx, (variant, results) in enumerate(variantResults.items()):
    # https://machinelearningmastery.com/precision-recall-and-f-measure-for-imbalanced-classification/

    #@TODO what do we do with invalid_response?

    print(f"\nVariant: {variant}")

    # Print out stats on individual classes
    data = sorted(results['individual'].items(), key=lambda item: item[0])

    # Note: we strip out accuracy because it doesn't work well on multiclass data
    
    rows = [
            ['All CWEs', *computeStats(results['aggregate'])[1:]],
            *[[cwe, *computeStats(freq)[1:]] for cwe, freq in data],
        ]

    prettyPrintTable(['CWE', 'Recall', 'Precision', 'F1'], rows)
            


print("\nComparison of Variants For CWE Classification:")
prettyPrintTable(['Variant', 'Recall', 'Precision', 'F1'], rows=[
    [variant, *computeStats(results['aggregate'])[1:]] for variant, results in variantResults.items()
])


plotFreq({variant:results['aggregate'] for variant, results in variantResults.items()}, forLabel='CWE Classification')

