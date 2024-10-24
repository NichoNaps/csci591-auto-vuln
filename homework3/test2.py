from z3 import *
import copy
from runner import parseSourceCode

class SymbolicState:

    def __init__(self):
        self.constraints = []
    
    # save a constraint to this state
    def addConstraint(self, constraint):
        self.constraints.append(constraint)
    
    def isFeasible(self):
        solver = Solver()

        for constr in self.constraints:
            solver.add(constr)
        
        return solver.check() == ast


    # shallow copy of the list of constraints so we can add more without
    # affecting the old list of older states
    def copy(self):
        new = SymbolicState()
        new.constraints = [*self.constraints]
    

    def __str__(self):
        return str(self.constraints)


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

    def __init__(self):

        # static scoping layers
        self.layers = [{}]

        self.current = SymbolicState()

    # define a variable on the current scope
    def defineVariable(self, varName):
        self.layers[-1][varName] = store.new(varName)
    
    def pushScope(self):
        self.layers.append({})

    def popScope(self):
        self.layers.pop()

    
    # get teh current z3 var object ofr this variable
    def getVariable(self, name):

        for layer in reversed(self.layers):
            if name in layer.keys():
                return layer[name]
    
    def print(self):

        print("\nScope:")
        for layer in self.layers:
            for varName, symbolicName in layer.items():
                print(f"{varName} => {symbolicName}")
            
    def copy(self):
        #@TODO
        newInterp = Interpreter()
        # newInterp.current = self.current # ????????????????


#@TODO, when we fork, the currentZ3 will get messed up when we finish going down one branch and go back to the other one.


# this uses the following example from in class
func_def = parseSourceCode(
"""
int f(int x, int y) {
    if (x > y) {
        x = x + y;
        y = x - y;
        x = x - y;

        if (x - y > 0) {
            return 0;
        }
    }

    return 1;
}
""", 'f')

print(func_def)

interp = Interpreter()

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


exit()

A = Int('A') 
B = Int('B')  

x1 = Int('x1')  
y1 = Int('y1')

x2 = Int('x2')
y2 = Int('y2')

x3 = Int('x3') 
y3 = Int('y3')  

x_final = Int('x_final')  # after x++

# 
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
