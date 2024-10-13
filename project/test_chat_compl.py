
from llama_cpp import Llama # for usage see https://llama-cpp-python.readthedocs.io/en/latest/, https://github.com/abetlen/llama-cpp-python

# This example file uses the create_chat_completion api
# this adds the prompt format that Meta built llama3.1 with (it figures out which prompt format to use using the models metadata) 
# This is the format for llama3: https://github.com/meta-llama/llama3/blob/main/llama/tokenizer.py#L202-L229


llm = Llama.from_pretrained(
	repo_id="ggml-org/Meta-Llama-3.1-8B-Instruct-Q4_0-GGUF",
	filename="meta-llama-3.1-8b-instruct-q4_0.gguf",
    verbose=True, # to view info about ai as it runs and see accel mode
    #   n_gpu_layers=1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)


message_history = [
    {"role": "system", "content": "You are an assistant that helps answer trivia about automated vulnerability discovery techniques."},
]

while True:
    inp = input("Input: ")

    message_history.append(
        {
            "role": "user",
            "content": inp
        }
    )

    res = llm.create_chat_completion(messages=message_history)

    print("AI:", res['choices'][0]['message']['content'])


