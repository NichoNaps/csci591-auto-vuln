from domain import AbstractDomain
from parser import Parser
from worklist import worklist_algorithm


# define the zero analysis domain which is a simple diamond
domain = AbstractDomain([
    ('BOTTOM', 'Z'),
    ('BOTTOM', 'N'),
    ('Z', 'TOP'),
    ('N', 'TOP'),
])

# test with zero analysis, this is missing a lot of the operations but it works on prog_1.w3a
# apply node.instruction using node.inputs and save the result in node.output
def flow_zero_analysis(instruction, state) -> list[dict[str, str]]:
    outputs = state.copy()

    # AN EXCUSE TO USE PYTHON PATTERN MATCHING FINALLLLYYYY!!!!!!!! :)
    match instruction:

        # this returns two resulting states for true and false case
        # Remember this is always a comparison against a zero literal
        case ('if_goto', var, op, *_): 
            outputsTrue = outputs.copy()
            outputsFalse = outputs.copy()

            # If x = 0 then true means x = Z else x = N
            if op == '=':
                outputsTrue[var] = 'Z'
                outputsFalse[var] = 'N'

            elif op == '<':
                outputsTrue[var] = 'N'

                if state[var] != 'Z': #@TODO is this right?? only coerce to TOP if it isn't zero?
                    outputsFalse[var] = 'TOP'

            return [outputsTrue, outputsFalse]


        case ('assign_num', var, num):

            if num == 0:
                outputs[var] = 'Z'
            else:
                outputs[var] = 'N'

        case ('assign_var', var, varA):
            outputs[var] = state[varA]
        
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

            # We could add some division 0/1 here if we wanted

            # Give up and say its probably TOP
            else:
                outputs[var] = 'TOP'
    

    # return the one output
    return [outputs]


programLines = Parser("programs/prog_4.w3a").parse_program()

worklist_algorithm(programLines, domain, flow_zero_analysis)


