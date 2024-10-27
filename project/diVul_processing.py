import json

# Top 25 CWE list from Mitre 2021
top_25_cwes = {
    "CWE-787", "CWE-79", "CWE-125", "CWE-20", "CWE-78", "CWE-89", "CWE-416",
    "CWE-22", "CWE-352", "CWE-434", "CWE-306", "CWE-190", "CWE-502", "CWE-287",
    "CWE-476", "CWE-798", "CWE-119", "CWE-862", "CWE-276", "CWE-200", "CWE-522",
    "CWE-732", "CWE-611", "CWE-918", "CWE-77"
}

diversevul_top_25 = []

with open('diversevul_20230702.json', 'r') as file:
    # Due to errors, had to read file line by line
    for line in file:
        try:
            vuln = json.loads(line)
            if any(cwe in top_25_cwes for cwe in vuln.get("cwe", [])):
                diversevul_top_25.append(vuln)
        # Added this to avoid the errors in the file there does not appear to be any after reading
        # the JSON in line by line        
        except json.JSONDecodeError:
            print("Error in JSON")
            #print("Error in JSON line:", line)
            continue




# Save to a JSON file, adjust the token redability with indents
with open('diversevul_top_25.json', 'w') as file:
    json.dump(diversevul_top_25, file, indent=4)

print("Saved data saved to 'diversevul_top_25.json'")
