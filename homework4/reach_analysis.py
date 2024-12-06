from domain import AbstractDomain, produceSetPartialOrderRules
from parser import Program
from worklist import WorklistAlgo

# Page.29 https://cmu-program-analysis.github.io/2024/resources/program-analysis.pdf


def run_reach_analysis(program: Program):

    varAssigns = []
    for line_num, instruction in program.getLines():

        # gather all variable asssignments
        if 'assign' in instruction[0]:
            varAssigns.append(f"{instruction[1]}_{line_num}")

    print(f"Assignments: {varAssigns}")

    # Create a domain using these assignments
    BOTTOM, TOP, rules = produceSetPartialOrderRules(varAssigns)

    domain = AbstractDomain(rules)
    # domain.plot()


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


                return [outputsTrue, outputsFalse]


            case ('assign_num', var, num):

                # We assigned to a literal so reachability is reset to just this assignment
                outputs[var] = (f'{var}_{line_num}',)

            case ('assign_var', var, varA):
                current = (f'{var}_{line_num}',)

                # we assigned a var so append this assignment to the existing reachability of varA
                # print(f"{state[varA]} UNION {current}")
                outputs[var] = domain.join(state[varA], current) 

                # find all other places this vary is defined at
                killll = set([vary for vary in varAssigns if vary.startswith(var) and vary != current[0]])

                print('kill set', killll)
                print('gen set', outputs[var])

                # use kill set on all variables
                for key, gen in outputs.items():
                    outputs[key] = tuple(sorted(list(set(gen).difference(killll))))
                # input(outputs[var])
            
            case ('assign_op', var, varA, op, varB):
                current = (f'{var}_{line_num}',)

                # Joing this var assignment with the reachabilities of varA and varB
                # print(f"{state[varA]} {state[varB]} UNION {current}")
                outputs[var] = domain.join(current, domain.join(state[varB], state[varA])) # Just take the union of our reachabilities

                # find all other places this vary is defined at
                killll = set([vary for vary in varAssigns if vary.startswith(var) and vary != current[0]])

                print('kill set', killll)
                print('gen set', outputs[var])

                # use kill set on all variables
                for key, gen in outputs.items():
                    outputs[key] = tuple(sorted(list(set(gen).difference(killll))))
                # input(outputs[var])

        

        # return the one output
        return [outputs]

    # domain.plot()

    worklist = WorklistAlgo(program, domain, flow_reach_analysis, BOTTOM=BOTTOM)
    worklist.run()
    worklist.printStats(formatAbstractVal=lambda outputs: "{" + ", ".join([v for v in set([val for d in outputs for vals in d.values() for val in vals])]) + "}")


if __name__ == '__main__':

    run_reach_analysis(Program('programs/test_reach.w3a'))


