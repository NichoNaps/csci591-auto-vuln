

## Install Dependencies to run AI

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




