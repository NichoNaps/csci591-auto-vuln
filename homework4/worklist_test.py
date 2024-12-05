from domain import AbstractDomain
from parser import *



# define the zero analysis domain which is a simple diamond
domain = AbstractDomain([
    ('BOTTOM', 'Z'),
    ('BOTTOM', 'N'),
    ('Z', 'TOP'),
    ('N', 'TOP'),
])


def flow(node):
    # TODO apply node.instruction using node.inputs and save the result in node.output

    pass



result = Parser("programs/prog_1.w3a").parse_program()

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

        # if this is a goto statement it has two successive locations
        if self.instruction[0] in ['if_goto', 'goto']: 
            return [self.line_num, self.instruction[-1]]
        
        else:
            return [self.line_num]

    
    def __str__(self):
        return f"{self.line_num}: {self.instruction} \t Inputs:{self.inputs}, Outputs:{self.outputs}"
    


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

    node.output = flow(node)

    # Try adding successor lines as new work to do
    for childNode in [allNodes[i] for i in node.getSuccessors()]:

        newInputs = domain.joinStates(childNode.inputs, node.outputs)

        # if the inputs did indeed change, add this childNode as a new job
        if newInputs != childNode.inputs:
            childNode.inputs = newInputs
            worklist.append(childNode)
        






