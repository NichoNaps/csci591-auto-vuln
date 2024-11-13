
from llama_cpp import Llama # for usage see https://llama-cpp-python.readthedocs.io/en/latest/, https://github.com/abetlen/llama-cpp-python

# This example file uses the create_chat_completion api
# this adds the prompt format that Meta built llama3.1 with (it figures out which prompt format to use using the models metadata) 
# This is the format for llama3: https://github.com/meta-llama/llama3/blob/main/llama/tokenizer.py#L202-L229


llm = Llama.from_pretrained(
	repo_id="ggml-org/Meta-Llama-3.1-8B-Instruct-Q4_0-GGUF",
	filename="meta-llama-3.1-8b-instruct-q4_0.gguf",

	# repo_id="TheBloke/CodeLlama-7B-GGUF",
    # filename="codellama-7b.Q4_K_M.gguf",
    
	# repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
    # filename="codellama-7b-instruct.Q4_K_M.gguf", # pick the balanced quantized
    # chat_format="llama-2", # codellama is based on llama2 so use that format
    
    verbose=True, # to view info about ai as it runs and see accel mode
    #   n_gpu_layers=1, # Uncomment to use GPU acceleration
     # seed=1337, # Uncomment to set a specific seed
     n_ctx=30000, # @TODO we can raise this higher
)


message_history = [
        {"role": "system", "content": "Please determine the intent of the following code:"},
    ]

# Follow up prompt: I want you to act as a vulnerability detection system. Utilizing the intent of the code above, state whether or not the code is vulnerable/buggy. If it is vulnerable/buggy, specify where the vulnerability lies, and attempt to classify the vulnerability using Common Weakness Enumeration (CWE).

while True:

    inp = input("Input: ")
    inpCheck = inp
    res = "" 
    while inp != "SEND":
        res += inp + "\n"
        inp = input("Input: ")

    if inpCheck == "EXIT":
        print("Exiting....")
        break

    message_history.append(
            {
                "role": "user",
                "content": res
            }
    )

    # print(res)

    res = llm.create_chat_completion(messages=message_history)

    print("AI:", res['choices'][0]['message']['content'])


