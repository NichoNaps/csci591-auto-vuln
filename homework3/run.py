from pathlib import Path
import tree_sitter_c
from tree_sitter import Language, Parser

import argparse

# Ex: python run.py tests/test.c test

parser = argparse.ArgumentParser(prog='test', 
                                 description='A C symbolic executor. Analyzes a C file and tries to find the constraints needed to make a function return 1;')
parser.add_argument('filepath', type=Path, help='the path to the C file to parse') 
parser.add_argument('function', help='the name of the function to try getting return 1;') 

args = parser.parse_args()


with open(args.filepath, 'r') as f:
    source_code = f.read()

# load the c lang 
C_LANGUAGE = Language(tree_sitter_c.language())
parser = Parser(C_LANGUAGE)

tree = parser.parse(bytes(source_code, 'utf8'))

# print(tree.root_node)

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

# print(func_defs)

for func in func_defs:
    print("####################### Found Function:")
    # print(func)

    print('name:', func.child_by_field_name('declarator').child_by_field_name('declarator').text.decode())
    print('params:', func.child_by_field_name('declarator').child_by_field_name('parameters').text.decode())

    # print('body:', func.child_by_field_name('body'))

    # print(func.text)

    print("Function Source Code:")
    print(source_code[func.start_byte:func.end_byte])



