from z3 import *
import copy
from tree_sitter import Language, Parser, Tree, Node, TreeCursor
import random
from runner import parseSourceCode



# z3 want variables to be the same ie Int("x") != Int("x")
# storing this separately in a global store simplifies everything else so it
# doesn't have to deal with maintining the references etc when pushing and poping etc copying etc
class Z3Store:

    def __init__(self):
        self.store = {}

        self.freq = {}
    
    def new(self, startName):

        if startName in self.freq.keys():
            self.freq[startName] += 1
        else:
            self.freq[startName] = 0
        
        name = f"{startName}_{self.freq[startName]}"

        # assume everything is int
        self.store[name] = Int(name) 
    
        return name
    
    def get(self, name):
        return self.store[name]

# define global store
store = Z3Store()


class Interpreter:

    def __init__(self, node: Node):
        self.node = node # a node location in the source code to start executing from

        self.edgeConstraint = None # the edge condition to reach this symbolic state

        # static scoping/mapping layers
        self.layers = [{}]

        self.constraints = []
        self.children: list['Interpreter'] = []

        self.id = hex(random.randint(0, 999999999)) # Used for debugging only to keep track of what is what
    

    # test if the constraints we have accumulated are feasible
    def isFeasible(self):
        solver = Solver()

        for constr in self.constraints:
            solver.add(constr)
        
        return solver.check() == sat


    # define a variable on the current scope
    def defineVariable(self, varName):
        self.layers[-1][varName] = store.new(varName)
    
    # def assignVariable(self, varName, value):

    def pushScope(self):
        self.layers.append({})

    def popScope(self):
        self.layers.pop()

    
    # get the current z3 var name
    def getVariableZ3Name(self, name):
        for layer in reversed(self.layers):
            if name in layer.keys():
                return layer[name]
            
        raise Exception(f"Variable {name} doesn't exist!")


    # get the current z3 var object of this variable
    def getVariableZ3(self, name):
        return store.get(self.getVariableZ3Name(name))


    def __str__(self):
        res = f"Id: {self.id}\nConstraints:\n"
        for cons in self.constraints:
            res += f"{cons}\n"

        res += "\nMappings:\n"
        for idx, layer in enumerate(self.layers):
            res += f"Layer {idx}\n"

            for varName, symbolicName in layer.items():
                res += f"   {varName} => {symbolicName}\n"
        
        return res
    

    def print(self):
        print(str(self))


    def fork(self, treeCursor: TreeCursor, edgeConstraint):
        newInterp = Interpreter(treeCursor)
        newInterp.constraints = [*self.constraints, edgeConstraint] # create a new list but with the same restraint objects as before
        newInterp.edgeConstraint = edgeConstraint # save the edge constraint to this child
        newInterp.layers = copy.deepcopy(self.layers) # copy the current mapping/scope of variables but make sure it is completely dereferenced 

        self.children.append(newInterp)

        return newInterp
    

    #@TODO: this doesn't implement truthiness yet (integers == 0 are false, all other values are true)
    def parseConditionExpressionToZ3(self, exp: Node):

        print('Parsing Conditional Expression:', exp, ' -> ', exp.text.decode())

        if exp.type == 'parenthesized_expression':
            # @TODO is there something we need to do for parenthesis? and is it only one child always?
            return self.parseConditionExpressionToZ3(exp.children[1]) 
        
        elif exp.type == 'identifier':

            # evaluate identifiers to z3 variables
            z3Var = self.getVariableZ3(exp.text.decode())
            print(exp.text.decode(), ' -> ', z3Var)

            return z3Var

        elif exp.type == 'number_literal':
            return int(exp.text.decode())
        
        elif exp.type == 'binary_expression':

            leftHand = self.parseConditionExpressionToZ3(exp.child_by_field_name('left')) 
            rightHand = self.parseConditionExpressionToZ3(exp.child_by_field_name('right')) 

            operator = exp.children[1].text.decode()

            print('OPERATOR', operator)

            # convert all operators to z3 compliant ones
            if operator == '||':
                return Or(leftHand, rightHand)
            elif operator == '&&':
                return And(leftHand, rightHand)
            elif operator == '<':
                return leftHand < rightHand
            elif operator == '<=':
                return leftHand <= rightHand
            elif operator == '>':
                return leftHand > rightHand
            elif operator == '>=':
                return leftHand >= rightHand
            elif operator == '==':
                return leftHand == rightHand
            elif operator == '!=':
                return leftHand != rightHand
            else:
                raise Exception(f"Unknown operator {operator}") 
        else:
            raise Exception(f"Unknown exp node type {exp}") 


    def parseArithmeticExpressionToZ3(self, exp: Node):
        print('Parsing expression:', exp)
        #@TODO this should be similar to condition expression


    def run(self):

        self.print()
        print()

        # immediately stop if the constraints are infeasible
        if not self.isFeasible():
            print("INFEASIBLE!")
            return self


        while True:
            print(f'############ Found Node {self.node.type}: {self.node.text}')

            # enter compound statements automatically
            if self.node.type == 'compound_statement':
                self.node = self.node.children[0]

            elif self.node.type == 'if_statement':
                constraint = self.parseConditionExpressionToZ3(self.node.child_by_field_name('condition'))

                print('Got constraint from if statement:', constraint)

                # The fork if TRUE
                trueFork = self.fork(self.node.child_by_field_name('consequence'), constraint)

                print(self.node)

                # if false, check if there is an else clause to enter or if we should just move to the next statement
                elseClause = self.node.child_by_field_name('alternative')

                if elseClause is None:
                    newNode = self.node.next_sibling
                else:
                    newNode = elseClause.children[1]
                    print(elseClause.children)
                
                # the fork if FALSE
                falseFork = self.fork(newNode, Not(constraint))

                print(">>>>>>>>>>>> Starting TRUE Fork for", self.node.child_by_field_name('condition').text.decode())
                trueFork.run()
                print(">>>>>>>>>>>> Starting FALSE Fork for", self.node.child_by_field_name('condition').text.decode())
                falseFork.run()
                
                # Quit running this interpreter, the child interpreters have done everything
                return self


            elif self.node.type == 'declaration': # @TODO handle variable declaration
                dec = self.node.child_by_field_name('declarator')
                print(dec)

                # if its be declared and assigned a value
                if dec.type == 'init_declarator':
                    varName = dec.child_by_field_name('declarator').text.decode()
                    self.defineVariable(varName) # tell interpeter to define var

                    value = dec.child_by_field_name('value')
                    #@TODO turn value into a z3 constraint!

                    z3Value = self.parseArithmeticExpressionToZ3(value)

                    print(f"{varName} = {value}")

                else:
                    varName = dec.text.decode()
                    self.defineVariable(varName) # tell interpeter to define var


            # if we hit a return, then quit this interpreters interpretation
            elif self.node.type == 'return_statement':
                print(f"Function Returned {self.node.children[1].text.decode()}")

                #@TODO for the assignment we have to provide the constraints to reach 'return 1;'
                # i.e. we just have to show off this current interpreter/symbolic state somehow at the end maybe by marking 
                # it with a 'success' flag member field or something

                return self

            #@TODO when reaching the end of a code block, we need to check if it is a while loop
            # if so, we need to loop back, otherwise go up and to the next sibling
            elif self.node.type == '}': 

                
                while self.node.type == '}' or self.node.type == 'compound_statement' or self.node.type == 'if_statement':
                    self.node = self.node.parent

                    if self.node.next_sibling is not None:
                        self.node = self.node.next_sibling
                    
                    # sanity check
                    if self.node.type == 'function_definition':
                        raise Exception('Hit end of the program before a return statement. This c function is probably missing a return statement.')


                    print("Hit end of code block, going up node tree and then to the next sibling:")
                    print(self.node, self.node.text)
                    # input()


            # go to the next line
            else:
                self.node = self.node.next_sibling

            # input('Press enter to continue...')


    # Create a new interpreter and run it on a function
    @staticmethod
    def startOnFunction(func_def: Node) -> 'Interpreter':
        interp = Interpreter(func_def.child_by_field_name('body'))

        # find the parameters of the function
        params = [param for param in 
                func_def
                    .child_by_field_name('declarator')
                    .child_by_field_name('parameters').children 
                    if param.type == 'parameter_declaration']

        # define parameters as variables
        for param in params:
            paramName = param.child_by_field_name('declarator').text.decode()
            interp.defineVariable(paramName)

        interp.print()

        interp.run()

        return interp
        

if __name__ == "__main__":

    # this uses the following example from in class
    func_def = parseSourceCode(
    """
    int f(int x, int y) {

        if (x > y) {
            x = x + y;
            y = x - y;
            x = x - y;

            if (x > y) {
                return 0;
            }
        }
    

        return 1;
    }
    """, 'f')


    res = Interpreter.startOnFunction(func_def)






    exit()

    A = Int('A') 
    B = Int('B')  

    x1 = Int('x1')  
    y1 = Int('y1')

    x2 = Int('x2')
    y2 = Int('y2')

    x3 = Int('x3') 
    y3 = Int('y3')  

    x_final = Int('x_final') 


    solver = Solver()

    solver.add(x1 == A)
    solver.add(y1 == B)

    solver.add(x1 > y1) # the if statement

    solver.add(x2 == x1 + y1)

    solver.add(y2 == x2 - y1)

    solver.add(x3 == x2 - y2)

    solver.add(x_final == x3 + 1)

    # the if statement isn't satifiable like we want!!
    # solver.add(x_final - y2 > 0)

    if solver.check() == sat:
        print("sat")
    else:
        print("Constraints are unsatisfiable.")
