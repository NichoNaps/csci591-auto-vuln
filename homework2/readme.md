# Introduction
This is a fuzzer implemented in python for fuzzing the class provided mock mail server voidsmtpd. Fuzzing is a dynamic code analysis tool in cyber security that attempts to trigger program crashes/errors by sending malformed inputs. Once a crash is found, researchers can then look into exactly what caused the program to error out and if that error is its self a vulnerability (crashing a website's servers for example onto itself could be considered an exploit) or if a more intentionally crafted input could trigger a vulnerability in the program when it errors out like expose user data. 

See `logs/*` for examples of the program in action.

# Layout
- `harness.py` contains code to run the voidsmtpd binary, send inputs to it over telnet, and save reports of crashes to `./log/crashes/`. Expects the binary for voidsmtpd to be in the same folder as it and for telnet to be available.
- `FunctionMethod.py` contains input generation and runs the inputs it generates through the harness to test them out.
- `triage.py` is a script to parse over crash reports in `./log/crashes/` and tries to categorize them to find the unique crashes and their reports.


# Usage
```sh

# This will run for a long time generating crash reports, hit ctrl+c when done.
python FuntionMethod.py 

# This parses through crash reports to try and find unique crashes and their reports.
python triage.py 

```




