
from llama_cpp import Llama # for usage see https://llama-cpp-python.readthedocs.io/en/latest/, https://github.com/abetlen/llama-cpp-python


llm = Llama.from_pretrained(
	repo_id="ggml-org/Meta-Llama-3.1-8B-Instruct-Q4_0-GGUF",
	filename="meta-llama-3.1-8b-instruct-q4_0.gguf",
    verbose=True, # to view info about ai as it runs and see accel mode
      n_gpu_layers=1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)

#  I have some example code here but we should probably look at the build int "Chat Completion" stuff 


context = ""

while True:
    userInput = input("Input: ")

    context += f"\nQuestion: {userInput}\nAnswer: "

    output = llm.create_completion(
        context, # Prompt
        max_tokens=64, # Generate up to 64 tokens, set to None to generate up to the end of the context window
        stop=["Question:"], # Stop generating just before the model would generate a new question
        echo=False # Echo the prompt back in the output
    ) # Generate a completion, can also call create_completion

    text = output['choices'][0]['text'] 

    context += f"\nAI: {text}"

    print(f"AI: {text}")
