from harness import Harness, fileToJson
import re
import json

if __name__=="__main__":
    harness = Harness()


    positions_regex = re.compile("#[0-9]\s|.*?\/([0-9A-Za-z_\\.-]*\+0x[0-9a-z]*)")


    # collect same crashes together
    crashTypes = {}

    for report in harness.crashesPath.iterdir():
        data = fileToJson(report)

        serverLogs = '\n'.join(data['outputs']['server'])


        serverLogs = serverLogs.rsplit("=================================================================")[1]

        # grab only the first stack trace because sometimes there are multiple which differ desite the actual error being the same
        serverLogs = "   #0 0x" + serverLogs.split("   #0 0x")[1] 
        
        # extract the positions in the stacktrace to uniquely identify crashes ex: filename+0xas234g 
        positions = positions_regex.findall(serverLogs)


        id = tuple(positions)

        if id not in crashTypes.keys():
            crashTypes[id] = []

        crashTypes[id].append(report)


    # this script is not perfect at finding unique crashes 
    print(f"Probably :) Found {len(crashTypes.keys())} unique crashes")

    for typ, reportPaths in crashTypes.items():

        print(f"\n{typ}")

        print(f"Has {len(reportPaths)} total reports. Here are the first few by shortest input length:")
        

        # sort the reports by the input length
        reportJsons = [(path, fileToJson(path)) for path in reportPaths]
        reportJsons = sorted(reportJsons, key=lambda data: len("".join(data[1]['inputs'])))


        for path, data in reportJsons[:10]:
            print(path)
            # print("Input Length:", len("".join(data['inputs'])))
    
 