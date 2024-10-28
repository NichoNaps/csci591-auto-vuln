Assignment: https://www.cs.montana.edu/revelle/csci591/assignments/03/


# Setup

```sh
pip install tree-sitter tree-sitter-c z3-solver
```


See docs:
https://github.com/tree-sitter/py-tree-sitter
https://ericpony.github.io/z3py-tutorial/guide-examples.htm





## Tree Sitter Node Usage
```python
# you can print the structure (the type of a node and its named children)
print(node)

# you can jump to named children with this function:
myPotatoNode = node.child_by_field_name('potato')

# you can print the text of a node (it returns bytes so call .decode() to convert it back to a string)
print(node.text.decode())

# A Node in treesitter has children you can iterate over. 
# This includes both the named children seen above and any unnamed children
for child in node.children:
    print(child)

```
