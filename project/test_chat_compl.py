
from llama_cpp import Llama # for usage see https://llama-cpp-python.readthedocs.io/en/latest/, https://github.com/abetlen/llama-cpp-python
import json

# This example file uses the create_chat_completion api
# this adds the prompt format that Meta built llama3.1 with (it figures out which prompt format to use using the models metadata) 
# This is the format for llama3: https://github.com/meta-llama/llama3/blob/main/llama/tokenizer.py#L202-L229

class LLM: 

    def __init__(self, verbose = False):
        self.llm = Llama.from_pretrained(
            repo_id="ggml-org/Meta-Llama-3.1-8B-Instruct-Q4_0-GGUF",
            filename="meta-llama-3.1-8b-instruct-q4_0.gguf",
            chat_format="llama-3",

            # repo_id="TheBloke/CodeLlama-7B-GGUF",
            # filename="codellama-7b.Q4_K_M.gguf",
            
            # repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
            # filename="codellama-7b-instruct.Q4_K_M.gguf", # pick the balanced quantized
            # chat_format="llama-2", # codellama is based on llama2 so use that format
            
            verbose=verbose, # to view info about ai as it runs and see accel mode
            #   n_gpu_layers=1, # Uncomment to use GPU acceleration
            # seed=1337, # Uncomment to set a specific seed
            n_ctx=30000, # @TODO we can raise this higher
        )

        self.message_history = []


    def send(self, msg: str, role='user'):
        self.message_history.append({'role': role, 'content': msg.strip()})


    def clearHistory(self):
        self.message_history = []


    # pretty print message history for debugging
    def printHistory(self):
        print(json.dumps(self.message_history, indent=2))


    # get response from llm
    def getResponse(self):

        res = self.llm.create_chat_completion(messages=self.message_history)

        addedMsg = res['choices'][0]['message']

        # save what the llm said 
        self.message_history.append(addedMsg)

        return addedMsg['content'].strip()



if __name__ == "__main__":
    llm = LLM(verbose=True)
    llm.send('Please determine the intent of the following code:', role='system')

    while True:

        inp = input("Input: ")
        inpCheck = inp
        res = "" 
        while inp != "SEND":
            res += inp + "\n"
            inp = input("Input (Send SEND to finally send the message): ")

        if inpCheck == "EXIT":
            print("Exiting....")
            break

        llm.send(res)

        response = llm.getResponse()

        llm.printHistory()

        print("AI:", response)


