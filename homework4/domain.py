
import networkx as nx


# Define a domain lattice with partial order rules.
# Meaning its the conversion rules for what is a subset of what.
# @NOTE: Only supports going up or staying on the same type level (lose information or stay the same)
# @NOTE: Only support going to a third super type if it is one hop up, which should be good enough for this assignment
class AbstractDomain:

    def __init__(self, rules: list[tuple[str, str]]):
        self.graph = nx.DiGraph()
        self.graph.add_edges_from(rules)

    def join(self, typeA: str, typeB: str) -> str:
        if typeA == typeB:
            return typeA
        
        # If A is a subset of B
        if nx.has_path(self.graph, typeA, typeB):
            return typeB
        
        # if B is a subset of A
        if nx.has_path(self.graph, typeB, typeA):
            return typeA


        # at this point neither is of a subset of one another so try digging up to the type using the fewest jumps
        shortestDist = None
        superType = None
        for node in self.graph.nodes:
            
            # if both types can reach it
            try:
                dist = nx.shortest_path_length(self.graph, typeA, node) + nx.shortest_path_length(self.graph, typeB, node)

                if shortestDist is None or dist < shortestDist:
                    shortestDist = dist
                    superType = node


            # Ignore if no path exists
            except nx.exception.NetworkXNoPath:
                pass

        # if we found no super type throw error
        if superType is None:
            raise Exception(f"Unsupported join between {typeA} and {typeB}")

        
        return superType
    

    # Plot for debugging
    def plot(self):
        import matplotlib.pyplot as plt
        import numpy as np
        import tkinter

        plt.figure(figsize=(8, 6))

        pos = nx.shell_layout(self.graph)  # Layout for better visualization
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color="powderblue")
        nx.draw_networkx_edges(self.graph, pos, edge_color="black", arrows=True)
        plt.title("Partial Order Graph")
        plt.show()


if __name__ == "__main__":

    # define the zero analysis domain which is a simple diamond
    domain = AbstractDomain([
        ('BOTTOM', 'Z'),
        ('BOTTOM', 'N'),
        ('Z', 'TOP'),
        ('N', 'TOP'),
    ])
    # domain.plot()

    assert domain.join('Z', 'Z') == 'Z'

    # if one is a subset of the other take the larger one
    assert domain.join('BOTTOM', 'Z') == 'Z'
    assert domain.join('Z', 'TOP') == 'TOP'
    
    # joining should allow multiple hops
    assert domain.join('BOTTOM', 'TOP') == 'TOP'

    # joining these types requires going to the super type TOP
    assert domain.join('Z', 'N') == 'TOP'
    assert domain.join('N', 'Z') == 'TOP'




