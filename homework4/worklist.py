from domain import AbstractDomain
from parser import *


# Represents a line in the program within the worklist algorithm
class Node:

    def __init__(self, line_num, instruction):
        self.line_num: int = line_num
        self.instruction: tuple = instruction

        # these are initilized elseware
        self.inputs = None
        self.outputs = None
    
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
    


# Worklist algorithm based on page 25 of https://cmu-program-analysis.github.io/2024/resources/program-analysis.pdf
def worklist_algorithm(programLines, domain: AbstractDomain, flowFunction: callable):

    # First initialize all nodes by their line number for reference
    allNodes = {}
    allVarNames = []
    for line_num, instruction in programLines:
        allNodes[line_num] = Node(line_num, instruction)

        # gather all variable names
        if 'assign' in instruction[0] and instruction[1] not in allVarNames:
            allVarNames.append(instruction[1])


    # creates a new state dictionary with all variables initialized to BOTTOM 
    def makeNewState():
        return {varName:'BOTTOM' for varName in allVarNames}


    worklist: list[Node] = []

    # add all nodes/lines of code once so each is visited at least once
    for node in allNodes.values():
        print('Initializing Line ', node)

        node.inputs = makeNewState()
        node.outputs = makeNewState()
        worklist.append(node)

    # allNodes[0].input = initialDataflowInformation???


    while len(worklist) > 0:

        node = worklist.pop(0)

        print(f"\n\n########## Running on {node}")

        # updates node.outputs using node.inputs following some flow analysis
        node.outputs = flowFunction(node.instruction, node.inputs) 

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
                    print("Already in worklist") # we can skip adding it if it is already in the worklist
            




