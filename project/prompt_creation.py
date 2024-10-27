# This is a start to prompt creation from the data set. Things we should consider adding: 
# More prompt structures, randomization on other prompts and on the vulns used from the data set.

import json

# use the top 25 data set
with open('diversevul_top_25.json', 'r') as file:
    diversevul_top_25 = json.load(file)

# If you want to limit the number of prompts generated
# set limit to true and select the number of prompts, otherwise set limit to false
limit = True
prompt_limit = 10

basic_prompts = []

for vuln in diversevul_top_25:

    cwes = vuln.get("cwe", [])
    func = vuln.get("func") 

    for cwe in cwes:
        prompt = f"Here is an example of {cwe} vulnerability and the code: \n{func} \nClassify the following code: \n{func}"
        basic_prompts.append(prompt)

    if (limit):
        if len(basic_prompts) >= prompt_limit:
            break

# save to new txt file "prompts.txt"
with open('prompts.txt', 'w') as f:
    for prompt in basic_prompts:
        f.write(prompt + '\n\n')

print("Prompts generated and saved to 'prompts.txt'")