from domain import AbstractDomain, produceSetPartialOrderRules
from parser import Parser
from worklist import worklist_algorithm

programLines = Parser("programs/prog_1.w3a").parse_program()

# Page.29 https://cmu-program-analysis.github.io/2024/resources/program-analysis.pdf


varAssigns = []
for line_num, instruction in programLines:

    # gather all variable asssignments
    if 'assign' in instruction[0]:
        varAssigns.append(f"{instruction[1]}_{line_num}")

print(f"Assignments: {varAssigns}")

# Create a domain using these assignments
BOTTOM, TOP, rules = produceSetPartialOrderRules(varAssigns)

domain = AbstractDomain(rules)
domain.plot()


# test with zero analysis, this is missing a lot of the operations but it works on prog_1.w3a
# apply node.instruction using node.inputs and save the result in node.output
def flow_reach_analysis(line_num, instruction, state) -> list[dict[str, str]]:
    outputs = state.copy()

    match instruction:

        # this returns two resulting states for true and false case
        # Remember this is always a comparison against a zero literal
        case ('if_goto', var, op, *_): 
            outputsTrue = outputs.copy()
            outputsFalse = outputs.copy()

            #@TODO

            return [outputsTrue, outputsFalse]


        case ('assign_num', var, num):

            # We assigned to a literal so reachability is reset to just this assignment
            outputs[var] = (f'{var}_{line_num}',)

        case ('assign_var', var, varA):

            # we assigned a var so append this assignment to the existing reachability of varA
            outputs[var] = domain.join(state[varA], (f'{var}_{line_num}',)) # 
        
        case ('assign_op', var, varA, op, varB):

            # Joing this var assignment with the reachabilities of varA and varB
            outputs[var] = domain.join((f'{var}_{line_num}',), domain.join(state[varB], state[varA])) # Just take the union of our reachabilities
    

    # return the one output
    return [outputs]


#@TODO do we need to do some inital set? what do we do in ifs???????
worklist_algorithm(programLines, domain, flow_reach_analysis, BOTTOM=BOTTOM)


