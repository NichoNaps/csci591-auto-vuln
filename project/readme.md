# Introduction
This is the source code for our group's chosen final project in automated vulnerability discovery. In it, we use Llama2 a large language model via llamacpp to do static code analysis on datasets including:
1) classify whether a snippet of code is vulnerable or not 
2) classify what kind of vulnerability a code snippet is (CWE)

See the full `Report.pdf` for reasoning, methodology, comparisons and results.

# Setup

## Setup Windows
On Windows I recommend running this all through WSL because it makes installing `llama-cpp-python` much easier because WSL comes with the neccesary dependencies.

To fit the LLM in RAM, you may need to manually specify the RAM size of WSL if it defaults too low (it defaults to half of your RAM). On a 16Gig windows computer we had to manually specify 12Gb.

From within WSL you can run the following to see the total amount of ram it has `free -m`.

### (Optionally) Increase WSL RAM Limit On Windows
Create the .wslconfig file if it doesnt exist here: `C:/Users/<username>/.wslconfig` 

File contents:
```toml
[wsl2]
memory=12GB
```

Then reset wsl from powershell with:
```sh
wsl --shutdown
```
The result of `free -m` should now be about the amount you specified in the config file.

## (Optionally) setup a virt environment
```sh
python -m venv env # create python virt env
source env/bin/activate # activate python virt env (You'll have to do this every time)
```

## Install Dependencies

We are downloading things from hugging face so we need this dependency.
```sh
pip install huggingface-hub
```

Dependencies needed for plotting
```sh
pip install matplotlib numpy # also potentially tk with: sudo apt install python3-tk
```

There are a bazillion ways to install llama-cpp-python depending on what kind of gpu/cpu support you want: https://llama-cpp-python.readthedocs.io/en/latest/. The following only installs basic CPU support.

```sh
install llama-cpp-python
```

- Add these pip flags if you need to re-install llama-cpp-python with diff cmake flags: `--no-cache-dir --force-reinstall`.



Here is an example of a modern x86 cpu with AVX2 support on linux. Without this it took ~500ms per token, with it it took ~100ms per token so about 5x better. **Most build environments should auto detect** so you don't have to manually specify this many flags.
```sh
# source: https://github.com/ollama/ollama/blob/main/llm/generate/gen_linux.sh
CMAKE_ARGS="-DBUILD_SHARED_LIBS=on -DCMAKE_POSITION_INDEPENDENT_CODE=on -DGGML_NATIVE=off -DGGML_OPENMP=off -DGGML_AVX=on -DGGML_AVX2=on -DGGML_AVX512=off -DGGML_FMA=on -DGGML_F16C=on" pip install llama-cpp-python --no-cache-dir --force-reinstall
```

# Usage
### Test Running a chatbot

```sh
python test_chat_compl.py
```

Send some inputs. Then Run one input that is just SEND all caps and then it will run those inputs. The reason we wait for SEND, is so you can paste multiple lines of code in.

## Usage of batch.py
batch.py runs both the CWE classification and Vulnerability detection tests.

```sh
# how to use batch:
python batch.py -h

# CWE classification running for chunk 1 of the data on both variants
python batch.py cwe 1 --variant chain-of-thought
python batch.py cwe 1 --variant in-context-learning

# vuln detection running on chunk 1 of the data on both variants
python batch.py vuln 1 --variant chain-of-thought
python batch.py vuln 1 --variant in-context-learning
```


## Plot results of batch.py
batch.py saves its results into ./results/. From there run plot_cwe.py or plot_vuln.py to calculate and plot the stats on that data including f1 scores etc.
```sh
python plot_cwe.py
python plot_vuln.py
```


# Layout
- `batch.py` - runs testing and contains all prompts used
- `test_chat_compl.py` - contains a wrapper class over llama-cpp-python to make it easer for our use case and contains a test runner for trying out an LLM.
- `util.py` - contains helper functions, variables, and classes for the rest of our code
- `plot_cwe.py` - plots stats on results of CWE classification
- `plot_vuln.py` - plots stats on results of vulnerability detection
- `results/` - a directory that batch.py saves results into
- `datasets/` - a directory containing all of the datasets used