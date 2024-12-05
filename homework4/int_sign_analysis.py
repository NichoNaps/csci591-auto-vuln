from domain import AbstractDomain
from parser import Program
from worklist import WorklistAlgo


def run_int_sign_analysis(program: Program):

    # define the zero analysis domain which is a simple diamond
    domain = AbstractDomain([
        ('BOTTOM', 'Z'),
        ('BOTTOM', 'N'),
        ('BOTTOM', 'P'),
        ('P', 'TOP'),
        ('Z', 'TOP'),
        ('N', 'TOP'),
    ])

    # test with zero analysis, this is missing a lot of the operations but it works on prog_1.w3a
    # apply node.instruction using node.inputs and save the result in node.output
    def flow_sign_evaluation(line_num, instruction, state) -> list[dict[str, str]]:
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
                elif num > 0:
                    outputs[var] = 'P'
                else:
                    outputs[var] = 'N'

            case ('assign_var', var, varA):
                outputs[var] = state[varA]

            case ('assign_op', var, varA, op, varB):
                # Subtraction
                # Subtract variable from self is always zero
                if op == '-' and varA == varB:
                    outputs[var] = 'Z'
                # Negative subtracted from positive
                elif op == '-' and varA == 'P' and varB == 'N':
                    outputs[var] = 'P'
                # Positive subtracted from negative
                elif op == '-' and varA == 'N' and varB == 'P':
                    outputs[var] = 'N'
                # subtracting zero from anything does nothing
                elif op == '-' and varB == 'Z':
                    outputs[var] = state[varA]
                # subtracting negative from zero is positive
                elif op == '-' and varA == 'Z' and varB == 'N':
                    outputs[var] = 'P'
                # subtracting positive from zero is negative
                elif op == '-' and varA == 'Z' and varB == 'P':
                    outputs[var] = 'N'

                # Addition
                # if you add a negative to a positive, TOP
                elif op == '+' and varA == 'P' and varB == 'N':
                    outputs[var] = 'TOP'
                # add a negative to positive, but da other way
                elif op == '+' and varA == 'N' and varB == 'P':
                    outputs[var] = 'TOP'
                # adding variable to itself does nothing in zero analysis
                elif op == '+' and varA == varB:
                    outputs[var] = state[varA]
                # if adding zero to another variable its just that variable
                elif op == '+' and state[varB] == 'Z':
                    outputs[var] = state[varA]
                # if adding zero to another variable but da other way
                elif op == '+' and state[varA] == 'Z':
                    outputs[var] = state[varB]

                # Multiplication
                # multiplying two positives is positive
                elif op == '*' and varA == 'P' and varB == 'P':
                    outputs[var] = 'P'
                # multiplying two negatives is positive
                elif op == '*' and varA == 'N' and varB == 'N':
                    outputs[var] = 'P'
                # multiplying positive by negative is negative
                elif op == '*' and varA == 'P' and varB == 'N':
                    outputs[var] = 'N'
                # multiplying negative by positive is negative
                elif op == '*' and varA == 'N' and varB == 'P':
                    outputs[var] = 'N'
                # multiplying anything by zero is zero
                elif op == '*' and (varA == 'Z' or varB == 'Z'):
                    outputs[var] = 'Z'

                # Division
                # Negatives or positives divided by themselves is positive
                elif op == '/' and (varA == varB and varA != 'Z'):
                    outputs[var] = 'P'
                # Positive divided by negative is negative
                elif op == '/' and varA == 'P' and varB == 'N':
                    outputs[var] = 'N'
                # Negative divided by positive is negative
                elif op == '/' and varA == 'N' and varB == 'P':
                    outputs[var] = 'N'
                # Anything divided by zero is BOTTOM - This is undefined
                elif op == '/' and varB == 'Z':
                    outputs[var] = 'BOTTOM'
                # Zero divided by anything other than zero is zero
                elif op == '/' and varA == 'Z' and varB != 'Z':
                    outputs[var] = 'Z'

                # Give up and say its probably TOP
                else:
                    outputs[var] = 'TOP'


        # return the one output
        return [outputs]


    worklist = WorklistAlgo(program, domain, flow_sign_evaluation)
    worklist.run()
    worklist.printStats()


if __name__ == '__main__':
    run_int_sign_analysis(Program('programs/prog_1.w3a'))



