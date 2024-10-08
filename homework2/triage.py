from harness import Harness
import re
import json

if __name__=="__main__":
    harness = Harness()


    # collect same crashes together
    crashTypes = {}

    for report in harness.crashesPath.iterdir():
        with open(report, 'r') as f:
            data = json.load(f)

        serverLogs = '\n'.join(data['outputs']['server'])

        serverLogs = serverLogs.rsplit("=================================================================")[1]
        
        # extract the positions in the stacktrace to uniquely identify crashes ex: filename+0xas234g 
        positions = re.findall("#[0-9]\s|.*?\/([0-9A-Za-z_\\.-]*\+0x[0-9a-z]*)", serverLogs)

        id = tuple(positions)


        if id not in crashTypes.keys():
            crashTypes[id] = []

        crashTypes[id].append(report)


    print(f"Found {len(crashTypes.keys())} unique crashes")

    for typ, reportPaths in crashTypes.items():

        print(f"\n{typ}")
        print(f"Has {len(reportPaths)} total reports. Here are the first 3:")
        for report in reportPaths[:3]:
            print(report)
    
 
