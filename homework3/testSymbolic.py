from z3 import *
import copy
from runner import parseSourceCode

# class Edge:
#     def __init__(self):
#         self.constraint 

# class SymbolicState:

#     def __init__(self):
#         self.variableStack = [{}] # stack of variables to support variable shadowing

#         self.edgesOut = [] # the edges leading to this symbolic states children
    
#     def newConstraint(self, variableName, constraint):
#         pass

#     def isFeasible(self):
#         pass

#     def print(self):
#         for idx, layer in enumerate(self.variableStack):
#             print("Layer", idx)

#             for variable, constraints in layer.items():

#                 print()

#     # Just to be sure, use deep copy to make sure all attributes of this obj
#     # are not 
#     def clone(self):
#         return copy.deepcopy(self)

    

# When we move passed an if statement it should create 2 branches, these two branches will have new constraints they gained depending on if they are possible or not,
# we need to eval these appended constraints to see if the state is possible (the constraints can be fullfilled) and give up if it is simply infeasible.
C_LANGUAGE, tree, func_defs = parseSourceCode("""
int
test(int x) {
  int y = 10;
                                              
  if (x > 10) {
    return 1;
  }

  return 0;
}
""")



def traverse_tree(node):

    # Detect node type
    if node.type == 'if_statement':
        print("If statement")
    elif node.type == 'while_statement':
        print("While loop")
    elif node.type == 'assignment_expression':
        print("assignment")
    elif node.type == 'declaration':
        print("variable declared")
    else:
        print("Uknown type")

    print(node.text)

    # Recursively check all children
    for child in node.children:
        traverse_tree(child)

# try parsing the body of the function
traverse_tree(func_defs[0].child_by_field_name('body'))