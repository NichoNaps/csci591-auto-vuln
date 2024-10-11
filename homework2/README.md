This is a fuzzer implemented in python for fuzzing voidsmtpd.

- `harness.py` contains code to run the voidsmtpd binary, send inputs to it over telnet, and save reports of crashes to `./log/crashes/`. Expects the binary for voidsmtpd to be in the same folder as it and for telnet to be available.
- `FunctionMethod.py` contains input generation and runs the inputs it generates through the harness to test them out.
- `triage.py` is a script to parse over crash reports in `./log/crashes/` and tries to categorize them to find the unique crashes and their reports.


## Usage
```sh

# this will run for a long time generating crash reports, hit ctrl+c when done.
python FuntionMethod.py 

# parse through crash reports to try and find unique crashes and their reports.
python triage.py 

```




