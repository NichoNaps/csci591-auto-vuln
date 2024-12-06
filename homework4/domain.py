
import networkx as nx


# Define a domain lattice with partial order rules.
# Meaning its the conversion rules for what is a subset of what.
# @NOTE: Only supports going up or staying on the same type level (lose information or stay the same)
class AbstractDomain:

    def __init__(self, rules: list[tuple[str, str]]):
        self.graph = nx.DiGraph()
        self.graph.add_edges_from(rules)

    # support printing
    def __str__(self):
        return f"Domain({', '.join(str(node) for node in self.graph.nodes)})"

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

                # print(f"Found Super Type: {typeA} and {typeB} fit in {node} in {dist}")

                if shortestDist is None or dist < shortestDist:
                    shortestDist = dist
                    superType = node


            # Ignore if no path exists
            except nx.exception.NetworkXNoPath:
                pass

        # if we found no super type throw error
        if superType is None:
            raise Exception(f"Unsupported join between {typeA} and {typeB}")

        # print("USING SUPER TYPE", superType)
        
        return superType

    
    # Bulk join all values in two state mappings {varname => value, ...}
    def joinStates(self, stateA: dict[str, str], stateB: dict[str, str]) -> dict[str, str]:
        res = {}

        assert stateA.keys() == stateB.keys() # keys should be same in both

        for key in stateA.keys(): 
            res[key] = self.join(stateA[key], stateB[key])
        
        return res


    # Plot for debugging
    def plot(self):
        import matplotlib.pyplot as plt
        import numpy as np
        import tkinter

        plt.figure(figsize=(8, 6))

        pos = nx.spring_layout(self.graph)  # Layout for better visualization

        # pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot") # use graphviz for its tree layout func
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color="powderblue")
        nx.draw_networkx_edges(self.graph, pos, edge_color="black", arrows=True)
        plt.title("Partial Order Graph")
        plt.show()


import itertools

# generate all possible subsets of varnames and their partial order rules
def produceSetPartialOrderRules(allVarNames: list[str]):
    allVarNames = sorted(allVarNames)
    rules = []

    for i in range(len(allVarNames)):
        for subset in itertools.combinations(allVarNames, i): 
            for subsetB in itertools.combinations(allVarNames, i + 1): # get the next largest subsets

                # print(subset, subsetB)

                # connect an empty subset as bottom
                if len(subset) == 1:
                    rules.append((tuple(), tuple(subset)))

                if set(subset).issubset(set(subsetB)):
                    rules.append((tuple(subset), tuple(subsetB)))

    return tuple(), tuple(allVarNames), rules
            

if __name__ == "__main__":
    BOTTOM, TOP, rules = produceSetPartialOrderRules(['A', 'B', 'C'])
    domain = AbstractDomain(rules)
    print(domain)
    # domain.plot()

    assert domain.join(tuple(), ('A',)) == ('A',)
    assert domain.join(('A', 'C'), ('B',)) == ('A', 'B', 'C') # go to largest super type
    assert domain.join(('C',), ('B',)) == ('B', 'C') # go to closest supertype


    # define the zero analysis domain which is a simple diamond
    domain = AbstractDomain([
        ('BOTTOM', 'Z'),
        ('BOTTOM', 'N'),
        ('Z', 'TOP'),
        ('N', 'TOP'),
    ])
    print(domain)
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


    assert domain.joinStates({'a': 'TOP'}, {'a': 'BOTTOM'}) == {'a': 'TOP'}


