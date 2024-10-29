import networkx as nx
import matplotlib.pyplot as plt
from test2 import Interpreter
from runner import parseSourceCode

# my tkinter install is messed up but this seems to make it work
import tkinter 


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


G = nx.DiGraph()


# Parse over the resulting symbolic states turning them into a directed graph with networkx
def parseRes(parent):

    for child in parent.children:

        print(child.id)
        G.add_node(child.id, label=str(child))
        G.add_edge(parent.id, child.id, label=child.edgeConstraint)

        parseRes(child)
    
G.add_node(res.id, label=str(res))
parseRes(res)


pos = nx.spring_layout(G, k=0.5, seed=1)

nx.draw(G, pos, with_labels=False, node_size=5000, node_shape="s", node_color="lightblue")

# Draw edge labels
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_color="red")

# Draw node labels
nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, "label"), font_color="blue", font_size=8)

plt.title("Symbolic Execution Diagram")
plt.show()
# plt.savefig("test.png", format="PNG")
# plt.close()