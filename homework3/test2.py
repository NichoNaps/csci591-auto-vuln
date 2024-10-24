from z3 import *
import copy

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
        for constr in self.constraints:
            print(constr)


class Interpreter:

    def __init__(self):

        # static scoping layers
        self.layers = [{}]

        self.current = SymbolicState()

    # define a variable on the current scope
    def defineVariable(self, varName):
        self.layers[-1][varName] = Variable(len(self.layers) -1, varName)
    
    def pushScope(self):
        self.layers.append({})

    def popScope(self):
        self.layers.pop()

    
    # get teh current z3 var object ofr this variable
    def getVariable(self, name):

        for layer in reversed(self.layers):
            if name in layer.keys():
                return layer[name]
            

    def copy(self):
        newInterp = Interpreter()
        # newInterp.current = self.current # ????????????????
        newInterp.layers = []


# class Variable:

#     def __init__(self, layerIdx, varName):

#         # this is all metadata to create more readable unique z3 var names
#         self.layerIdx = layerIdx
#         self.varName = varName
#         self.version = -1

#         # the current z3 variable object
#         self.current = None

#         self.createNewZ3()
    
#     # create a new z3 var version
#     def createNewZ3(self):
#         self.version += 1
#         self.current = Int(str(self))

#         return self.current
    
#     def __str__(self):
#         return f"{self.layerIdx}_{self.varName}_{self.version}"

#     # get the current z3 var 
#     def getCurrent(self):
#         return self.current

#     def copy(self):
#         # Keep self.current reference, but we want everything else to be its own de-referenced copy 
#         return copy.copy(self)
        
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




#@TODO, when we fork, the currentZ3 will get messed up when we finish going down one branch and go back to the other one.

store = Z3Store()
print(store.new('potato'))
print(store.get('potato_0'))

exit()
# this uses the following example from in class
"""
def f(x,y):

    if (x > y):
        x = x + y
        y = x - y
        x = x - y

        if (x - y > 0): # this is infeasible
            assert False

    return (x, y)
"""

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
