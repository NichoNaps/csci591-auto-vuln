from util import *
import matplotlib.pyplot as plt
import copy
import numpy as np
import tkinter # fix plt

# This file computes stats and plots vulnerability detection


# @TODO:
"""
1. (Mostly implemented) We can compute the f1 score/precision for just each class
2. compute the micro average to look at the overall performance. We use micro average because the dataset is imbalanced (has no CWE-306 for example)

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
                variantResults[variant]['individual'][cwe] = mergeFrequencies(variantResults[variant]['individual'][cwe], freq)

                # sum aggregate results
                variantResults[variant]['aggregate'] = mergeFrequencies(variantResults[variant]['aggregate'], freq)



for idx, (variant, results) in enumerate(variantResults.items()):

    # https://machinelearningmastery.com/precision-recall-and-f-measure-for-imbalanced-classification/

    #@TODO what do we do with invalid_response?

    # Print out stats on individual
    for cwe, freqs in results['individual'].items():

        print()
        print(variant, cwe)
        try:

            # higher is better for all of these
            recall = freqs['true_pos'] / (freqs['true_pos'] + freqs['false_neg'])
            precision = freqs['true_pos'] / (freqs['true_pos'] + freqs['false_pos'])
            F1 = 2 * (precision * recall) / (precision + recall) # f1 represents a combination of both precision and recall

            # print stats
            print(f"Recall: {recall}")
            print(f"Precision: {precision}")
            print(f"F1: {F1}")
        except:
            print("ERROR")


