

# Install Dependencies to run AI

On windows I recommend running this all through WSL because it makes installing `llama-cpp-python` much easier because WSL comes with the neccesary dependencies.

To fit the LLM in RAM, you may need to manually specify the RAM size of WSL if it defaults too low (it defaults to half of your RAM). On a 16Gig windows computer we had to manually specify 12Gb.

From within WSL you can run the following to see the total amount of ram it has `free -m`.

### (Optionally) Increase WSL RAM Limit
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


### (Optionally) setup a virt environment
```sh
python -m venv env # create python virt env
source env/bin/activate # activate python virt env (You'll have to do this every time)
```

### Install llama-cpp-python

We are downloading things from hugging face so we need this dependency.
```sh
pip install huggingface-hub
```

There are a bazillion ways to install llama-cpp-python depending on what kind of gpu/cpu support you want: https://llama-cpp-python.readthedocs.io/en/latest/. The following only installs basic CPU support.

```sh
install llama-cpp-python
```

- Add these pip flags if you need to re-install llama-cpp-python with diff cmake flags: `--no-cache-dir --force-reinstall`.



Here is an example of a modern x86 cpu with AVX2 support on linux. Without this it took ~500ms per token, with it it took ~100ms per token so about 5x better.
```sh
# source: https://github.com/ollama/ollama/blob/main/llm/generate/gen_linux.sh
CMAKE_ARGS="-DBUILD_SHARED_LIBS=on -DCMAKE_POSITION_INDEPENDENT_CODE=on -DGGML_NATIVE=off -DGGML_OPENMP=off -DGGML_AVX=on -DGGML_AVX2=on -DGGML_AVX512=off -DGGML_FMA=on -DGGML_F16C=on" pip install llama-cpp-python --no-cache-dir --force-reinstall
```

### Test running a chatbot

```sh
python test_chat_compl.py
```

Send some inputs. Then Run one input that is just SEND all caps and then it will run those inputs. The reason we wait for SEND, is so you can paste multiple lines of code in.

### Running a batch of chats

```sh
python batch.py
```

Will run each command listed in the file in a new instance of the model. Will automatically add "SEND" after each listed message, so it just requires a list of inputs.





