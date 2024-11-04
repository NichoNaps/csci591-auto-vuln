from pathlib import Path
import argparse

from interpreter import Interpreter

import tree_sitter_c
from tree_sitter import Language, Parser, Tree, Node

# This file contains the code for taking in command line arguments as specified 
# by the assignment but beyond that is just some testing with tree sitter currently


# Parses a string of source code using tree sitter
def parseSourceCode(source_code: str, target_func: str) -> Node:

    # load the c lang 
    C_LANGUAGE = Language(tree_sitter_c.language())
    parser = Parser(C_LANGUAGE)

    tree = parser.parse(bytes(source_code, 'utf8'))


    # first lets get all functions, we can then manually walk over the nodes using the func def nodes as root nodes
    func_defs = C_LANGUAGE.query("""
    (
        (function_definition
        declarator: (function_declarator 
                        declarator: (identifier) 
                    )
        ) @function.definition
    )
    """).captures(tree.root_node)['function.definition']


    # find the desired function
    for func in func_defs:
        fname = func.child_by_field_name('declarator').child_by_field_name('declarator').text.decode()

        if fname == target_func:
            return func

        # print('name:', )
        # print('params:', func.child_by_field_name('declarator').child_by_field_name('parameters').text.decode())

        # print("Function Source Code:")
        # print(source_code[func.start_byte:func.end_byte])

    raise Exception("Couldn't find target function")

# Ex: python runner.py tests/test.c test
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='test', 
                                    description='A subset of C symbolic executor. Analyzes a C file and tries to find the constraints needed to make a function return 1;')
    parser.add_argument('filepath', type=Path, help='the path to the C file to parse') 
    parser.add_argument('function', help='the name of the function to try getting return 1;') 

    args = parser.parse_args()

    with open(args.filepath, 'r') as f:
        source_code = f.read()

    func_def = parseSourceCode(source_code, args.function)

    res = Interpreter.startOnFunction(func_def)

    res.plot()
    
    res.print_stats()

