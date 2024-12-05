from domain import AbstractDomain
from parser import *


# Represents a line in the program within the worklist algorithm
class Node:

    def __init__(self, line_num, instruction):
        self.line_num: int = line_num
        self.instruction: tuple = instruction

        # these are initilized elseware
        self.input = None # singular input state
        self.outputs = None # list of output states
    
    # Return a list of the line numbers that come out from this instruction
    def getSuccessors(self) -> list[int]:

        match self.instruction:

            # halt has no successors
            case ('halt',):
                return [] 

            # goto a specified line
            case ('goto', *_):
                return [self.instruction[-1]]

            # if goto explores both the true and false case
            case ('if_goto', *_):
                return [self.instruction[-1], self.line_num + 1]

            # otherwise it is the next line
            case _:
                return [self.line_num + 1]

    
    def __str__(self):
        return f"{self.line_num}: {self.instruction}"
    


# Worklist algorithm based on page 25 of https://cmu-program-analysis.github.io/2024/resources/program-analysis.pdf
def worklist_algorithm(programLines, domain: AbstractDomain, flowFunction: callable, BOTTOM='BOTTOM'):

    # First initialize all nodes by their line number for reference
    allNodes: dict[int, Node] = {}
    allVarNames = []
    for line_num, instruction in programLines:
        allNodes[line_num] = Node(line_num, instruction)

        # gather all variable names
        if 'assign' in instruction[0] and instruction[1] not in allVarNames:
            allVarNames.append(instruction[1])


    # creates a new state dictionary with all variables initialized to BOTTOM 
    def makeNewState():
        return {varName:BOTTOM for varName in allVarNames}


    worklist: list[Node] = []

    # add all nodes/lines of code once so each is visited at least once
    for node in allNodes.values():
        print('Initializing Line ', node)

        node.input = makeNewState()
        node.outputs = makeNewState()
        worklist.append(node)

    # allNodes[0].input = initialDataflowInformation???


    while len(worklist) > 0:

        node = worklist.pop(0)

        print(f"\n\n########## Running on {node}")

        # updates node.outputs using node.input following some flow analysis
        node.outputs = flowFunction(node.line_num, node.instruction, node.input) 

        print('Flow Input:', node.input)
        print('Flow Outputs:', node.outputs)
        print()
        


        childNodes = [allNodes[i] for i in node.getSuccessors()]

        # Sanity check we have enough outputs
        if len(childNodes) > len(node.outputs):
            raise Exception(f"Expected {len(childNode)} many output states from flow function")


        # Try adding successor lines as new work to do
        for output, childNode in zip(node.outputs, childNodes):

            newInputs = domain.joinStates(childNode.input, output)

            # if the inputs did indeed change, add this childNode as a new job
            if newInputs != childNode.input:
                print(f"Added successor to worklist {childNode} with inputs: {newInputs}")
                childNode.input = newInputs

                if childNode not in worklist:
                    worklist.append(childNode)
                else:
                    print("Already in worklist") # we can skip adding it if it is already in the worklist
            




