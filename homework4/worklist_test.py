from domain import AbstractDomain
from parser import *



# define the zero analysis domain which is a simple diamond
domain = AbstractDomain([
    ('BOTTOM', 'Z'),
    ('BOTTOM', 'N'),
    ('Z', 'TOP'),
    ('N', 'TOP'),
])


# test with zero analysis
# apply node.instruction using node.inputs and save the result in node.output
def flow(instruction, state):
    outputs = state.copy()

    # AN EXCUSE TO USE PYTHON PATTERN MATCHING FINALLLLYYYY!!!!!!!! :)
    match instruction:

        case ('assign_num', var, num):

            if num == 0:
                outputs[var] = 'Z'
            else:
                outputs[var] = 'N'
        
        case ('assign_op', var, varA, op, varB):

            # Subtract variable from self is always zero
            if op == '-' and varA == varB: 
                outputs[var] = 'Z'

            # adding variable to itself does nothing in zero analysis
            if op == '+' and varA == varB: 
                outputs[var] = state[varA]

            # if adding zero to another variable its just that variable
            if op == '+' and state[varB] == 'Z':
                outputs[var] = state[varA]

            # Give up and say its probably TOP
            else:
                outputs[var] = 'TOP'
        
    return outputs



result = Parser("programs/prog_1.w3a").parse_program()

#@TODO we need to find all variable names dynamically
def makeState():
    return {'x': 'BOTTOM', 'y': 'BOTTOM'}

# Represents a line in the program within the worklist algorithm
class Node:

    def __init__(self, line_num, instruction):
        self.line_num: int = line_num
        self.instruction: tuple = instruction

        self.inputs = makeState()
        self.outputs = makeState()
    
    # Return a list of the line numbers that come out from this instruction
    def getSuccessors(self) -> list[int]:

        match self.instruction:

            # halt has no successors
            case ('halt',):
                return [] 

            # if this is a goto statement it has two successive locations
            case (('if_goto' | 'goto'), *_):
                return [self.line_num + 1, self.instruction[-1]]
        
            # otherwise it is the next line
            case _:
                return [self.line_num + 1]

    
    def __str__(self):
        return f"{self.line_num}: {self.instruction}"
    


# First initialize all nodes by their line number for reference
allNodes = {}
for line_num, instruction in result:
    allNodes[line_num] = Node(line_num, instruction)



worklist: list[Node] = []

# add all nodes/lines of code once so each is visited at least once
for node in allNodes.values():
    print('Initializing Line ', node)

    worklist.append(node)

# allNodes[0].input = initialDataflowInformation???


while len(worklist) > 0:

    node = worklist.pop(0)

    print(f"\n\n########## Running on {node}")

    # updates node.outputs using node.inputs following some flow analysis
    node.outputs = flow(node.instruction, node.inputs) 

    print('Flow Inputs:', node.inputs)
    print('Flow Outputs:', node.outputs)
    print()

    # Try adding successor lines as new work to do
    for childNode in [allNodes[i] for i in node.getSuccessors()]:

        newInputs = domain.joinStates(childNode.inputs, node.outputs)

        # if the inputs did indeed change, add this childNode as a new job
        if newInputs != childNode.inputs:
            print(f"Added successor to worklist {childNode} with inputs: {newInputs}")
            childNode.inputs = newInputs

            if childNode not in worklist:
                worklist.append(childNode)
            else:
                print("Already in worklist")
        






