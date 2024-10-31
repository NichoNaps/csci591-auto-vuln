from z3 import *
import copy
from tree_sitter import Language, Parser, Tree, Node, TreeCursor
import random
from runner import parseSourceCode


def forceInt(exp):

    if (exp.sort().kind() == Z3_BOOL_SORT):
        return If(exp, 1, 0)
    
    return exp

def forceBool(exp):

    if (exp.sort().kind() == Z3_INT_SORT):
        return If(exp == 0, False, True)
    
    return exp



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
    def defineVariable(self, varName, value = None):

        self.layers[-1][varName] = store.new(varName)

        # optionaly set an initial value to this variable
        if value is not None:
            self.constraints.append(store.get(self.layers[-1][varName]) == value)

    

    # incriments the name of the z3 variable that represents this variable
    # and adds a constraint for that variable representing an assignment
    def assignVariable(self, varName, value):
        for layer in reversed(self.layers):
            if varName in layer.keys():
                layer[varName] = store.new(varName) # create a new z3 variable

                # save the constraint of this assignment
                self.constraints.append(store.get(layer[varName]) == value)

                return 

        raise Exception(f"Variable {varName} doesn't exist!")


    def pushScope(self):
        self.layers.append({})

    def popScope(self):
        self.layers.pop()

    
    # get the current z3 var name
    def getVariableZ3Name(self, varName):
        for layer in reversed(self.layers):
            if varName in layer.keys():
                return layer[varName]
            
        raise Exception(f"Variable {varName} doesn't exist!")


    # get the current z3 var object of this variable
    def getVariableZ3(self, varName):
        return store.get(self.getVariableZ3Name(varName))


    def __str__(self):
        res = f"Id: {self.id}\n"
        res = f"On Line: {self.node.start_point[0] + 1}\n"
        res += "Constraints:\n"
        for cons in self.constraints:
            res += f"{cons}\n"

        if not self.isFeasible():
            res += f"INFEASIBLE\n"

        res += "\nMappings:\n"
        for idx, layer in enumerate(self.layers):
            res += f"Layer {idx}\n"

            for varName, symbolicName in layer.items():
                res += f"   {varName} => {symbolicName}\n"
        
        return res
    

    def print(self):
        print(str(self))


    def fork(self, treeCursor: TreeCursor, edgeConstraint) -> 'Interpreter':
        newInterp = Interpreter(treeCursor)
        newInterp.constraints = [*self.constraints, edgeConstraint] # create a new list but with the same restraint objects as before
        newInterp.edgeConstraint = edgeConstraint # save the edge constraint to this child
        newInterp.layers = copy.deepcopy(self.layers) # copy the current mapping/scope of variables but make sure it is completely dereferenced 

        self.children.append(newInterp)

        return newInterp
    

    def plot(self):
        # pip install pygraphviz networkx matplotlib 
        # apt install pyhton3-tk ??
        # apt install graphviz ???
        
        import networkx as nx
        import matplotlib.pyplot as plt
        # my tkinter install is messed up but this seems to make it work
        import tkinter 

        G = nx.DiGraph()

        # Parse over the resulting symbolic states turning them into a directed graph with networkx
        def parseRes(parent):

            for child in parent.children:

                print(child.id)
                G.add_node(child.id, label=str(child))
                G.add_edge(parent.id, child.id, label=child.edgeConstraint)

                parseRes(child)
            
        G.add_node(self.id, label=str(self))
        parseRes(self)


        # pos = nx.spring_layout(G, k=0.5, seed=1)
        # pos = nx.shell_layout(G)
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot") # use graphviz for its tree layout func

        nx.draw(G, pos, with_labels=False, node_size=5000, node_shape="s", node_color="lightblue")

        # Draw edge labels
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_color="red")

        # Draw node labels
        nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, "label"), font_color="blue", font_size=8)

        plt.title("Symbolic Execution Diagram")
        plt.show()
        # plt.savefig("test.png", format="PNG")
        # plt.close()



    # Parse a tree sitter node expression into a z3 constraint expression
    def parseExpressionToZ3(self, exp: Node):

        print('Parsing Expression:', exp, ' -> ', exp.text.decode())

        if exp.type == 'parenthesized_expression':
            # @TODO is there something we need to do for parenthesis? and is it only one child always?
            return self.parseExpressionToZ3(exp.children[1])
        
        elif exp.type == 'identifier':

            # evaluate identifiers to z3 variables
            z3Var = self.getVariableZ3(exp.text.decode())
            print(exp.text.decode(), ' -> ', z3Var)

            return z3Var

        elif exp.type == 'number_literal':
            return IntVal(int(exp.text.decode()))
        
        elif exp.type == 'binary_expression':

            leftHand = self.parseExpressionToZ3(exp.child_by_field_name('left')) 
            rightHand = self.parseExpressionToZ3(exp.child_by_field_name('right')) 


            operator = exp.children[1].text.decode()

            print('OPERATOR', operator)

            # convert all operators to z3 compliant ones
            if operator == '||':
                return Or(forceBool(leftHand), forceBool(rightHand))
            elif operator == '&&':
                return And(forceBool(leftHand), forceBool(rightHand))
            elif operator == '<':
                return forceInt(leftHand) < forceInt(rightHand)
            elif operator == '<=':
                return forceInt(leftHand) <= forceInt(rightHand)
            elif operator == '>':
                return forceInt(leftHand) > forceInt(rightHand)
            elif operator == '>=':
                return forceInt(leftHand) >= forceInt(rightHand)
            elif operator == '==':
                return forceInt(leftHand) == forceInt(rightHand)
            elif operator == '!=':
                return forceInt(leftHand) != forceInt(rightHand)
            elif operator == '+':
                return forceInt(leftHand) + forceInt(rightHand)
            elif operator == '-':
                return forceInt(leftHand) - forceInt(rightHand)
            elif operator == '*':
                return forceInt(leftHand) * forceInt(rightHand)
            elif operator == '/':
                return forceInt(leftHand) / forceInt(rightHand)
            else:
                raise Exception(f"Unknown operator {operator}") 
        else:
            raise Exception(f"Unknown exp node type {exp}") 

    # has a constraint for the number of iterations to avoid explosion
    def handleWhileLoop(self):
        print("######################## Handling While Loop")

        constraint = forceBool(self.parseExpressionToZ3(self.node.child_by_field_name('condition')))

        print('while loop constraint:', constraint)

        # fork that enters the while loop
        trueFork = self.fork(self.node.child_by_field_name('body'), constraint)

        # fork that continues after this while loop
        falseFork = self.fork(self.node.next_sibling, Not(constraint))

        print(">>>>>>>>>>>> Starting TRUE Fork for", self.node.child_by_field_name('condition').text.decode())
        trueFork.run()

        print(">>>>>>>>>>>> Starting FALSE Fork for", self.node.child_by_field_name('condition').text.decode())
        falseFork.run()


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
                self.pushScope()

            elif self.node.type == 'if_statement':
                constraint = forceBool(self.parseExpressionToZ3(self.node.child_by_field_name('condition')))

                print('Got constraint from if statement:', constraint)


                # The fork if TRUE
                trueNode = self.node.child_by_field_name('consequence')
                trueFork = self.fork(trueNode, constraint)

                # if false, check if there is an else clause to enter or if we should just move to the next statement
                elseClause = self.node.child_by_field_name('alternative')

                if elseClause is None:
                    falseNode = self.node.next_sibling
                else:
                    falseNode = elseClause.children[1]
                    print(elseClause.children)
                
                # the fork if FALSE
                falseFork = self.fork(falseNode, Not(constraint))

                print(">>>>>>>>>>>> Starting TRUE Fork for", self.node.child_by_field_name('condition').text.decode())
                trueFork.run()

                print(">>>>>>>>>>>> Starting FALSE Fork for", self.node.child_by_field_name('condition').text.decode())
                falseFork.run()
                
                # Quit running this interpreter, the child interpreters have done everything
                return self

            # Variable declaration ex: int a = 5;
            elif self.node.type == 'declaration':
                dec = self.node.child_by_field_name('declarator')
                print(dec)

                # if its be declared and assigned a value
                if dec.type == 'init_declarator':
                    varName = dec.child_by_field_name('declarator').text.decode()
                    value = forceInt(self.parseExpressionToZ3(dec.child_by_field_name('value')))


                    print(f"Performing Declaration {varName} = {value};")
                    self.defineVariable(varName, value)

                else:
                    varName = dec.text.decode()

                    print(f"Performing Declaration {varName};")
                    self.defineVariable(varName) # tell interpeter to define var


                # now go to next line!!!
                self.node = self.node.next_sibling


            # Variable Assignment ex: a = 5;
            elif self.node.type == 'expression_statement':
                assignment = self.node.children[0]

                varName = assignment.child_by_field_name('left').text.decode()
                value = forceInt(self.parseExpressionToZ3(assignment.child_by_field_name('right')))

                print(f"Performing Assignment: {varName} = {value};")

                self.assignVariable(varName, value)


                # now go to next line!!!
                self.node = self.node.next_sibling


            # if we hit a return, then quit this interpreters interpretation
            elif self.node.type == 'return_statement':
                print(f"Function Returned {self.node.children[1].text.decode()}")

                #@TODO for the assignment we have to provide the constraints to reach 'return 1;'
                # i.e. we just have to show off this current interpreter/symbolic state somehow at the end maybe by marking 
                # it with a 'success' flag member field or something

                return self

            # if we hit a while loop:
            elif self.node.type == 'while_statement':
                self.handleWhileLoop() 
                return self


            # When reaching the end of a code block, we need to check if it is a while loop
            # if so, we need to loop back, otherwise go up and to the next sibling
            elif self.node.type == '}': 

                
                while self.node.type == '}' or self.node.type == 'compound_statement' or self.node.type == 'if_statement':
                    if self.node.type == '}':
                        self.popScope()

                    print("Hit end of code block, going up node tree and then to the next sibling:")


                    self.node = self.node.parent


                    # Check for a while loop before we try moving to the next line
                    if self.node.type == 'while_statement':
                        self.handleWhileLoop()
                        return self


                    # Sanity check
                    if self.node.type == 'function_definition':
                        raise Exception('Hit end of the program before a return statement. This c function is probably missing a return statement.')


                    # try moving to the next line
                    if self.node.next_sibling is not None:
                        self.node = self.node.next_sibling

                        # if we encountered a if statement by going to the next,
                        # this is a valid next thing to run on so escape this loop
                        if self.node.type == 'if_statement':
                            print(self.node, self.node.text)

                            break
                    
                    

                    print(self.node, self.node.text)
                    # input()


            # now go to the next line!!
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

        interp.run()

        return interp
        

if __name__ == "__main__":

    # this uses the following example from in class
    func_def = parseSourceCode(
    """
    int f(int x, int y) {
        int z = 5;

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

    # ++x
    solver.add(x == x + 1)
    # --x
    solver.add(x == x - 1)

    # x++ create two values, to simulate c? 

    x = Int('x')
    x_og = Int('x_og')

    solver.add(x_og = x) # save the value of x
    solver.add(x == x + 1) # x++

    # x-- same as x++ but change last line to:
    solver.add(x == x - 1) # x--
    

    # the if statement isn't satifiable like we want!!
    # solver.add(x_final - y2 > 0)

    if solver.check() == sat:
        print("sat")
    else:
        print("Constraints are unsatisfiable.")
