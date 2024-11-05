Assignment: https://www.cs.montana.edu/revelle/csci591/assignments/03/


# Setup

```sh
pip install tree-sitter tree-sitter-c z3-solver

# for plotting:
#sudo apt install graphviz
sudo apt install python3-tk
sudo apt install libgraphviz-dev

pip install pygraphviz networkx matplotlib 
```

# Usage

```sh
# to test the function 'test' in a c file:
python runner.py ./tests/real_test.c test

# to run one of our builtin tests
python test_while.py
```


# Layout
- `interpreter.py` The main file with all the interpreter logic.
- `runner.py` The file that takes command line args to open a C file and run it with the interpreter.
- `test_*.py` are python files that run a specific test of C code.




# Misc

See docs:
https://github.com/tree-sitter/py-tree-sitter
https://ericpony.github.io/z3py-tutorial/guide-examples.htm

## Tree Sitter Node Usage
```python
# you can print the structure (the type of a node and its named children)
print(node)

# you can print the text of a node (it returns bytes so call .decode() to convert it back to a string)
print(node.text.decode())

# you can jump to named children with this function:
myPotatoNode = node.child_by_field_name('potato')

# A Node in treesitter has children you can iterate over. 
# This includes both the named children seen above and any unnamed children
for child in node.children:
    print(child)

# get the first child
firstChild = node.children[0]

# you can get the next sibling or parent of nodes too
theNextNode = node.next_sibling
theParentNode = node.parent

```
