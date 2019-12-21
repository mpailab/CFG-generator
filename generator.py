from random import choice, randint, shuffle
from grammar import CFG
from tree import Tree

def run (grammar, depth, size = 1000000):
    assert ( isinstance(grammar, CFG) and isinstance(depth, int) and isinstance(size, int) )
    skip_prods = grammar.skip_prods()
    tree = Tree(grammar.start())
    while tree.size() < size:
        leaves = tree.leaves(depth)
        if leaves:
            shuffle(leaves)
            k = randint(1, len(leaves))
                prod = choice(grammar.symbol_prods(node.symbol))
                tree.insert(node, prod)
        else:
            skip_nodes = tree.skips()
            if skip_prods and skip_nodes:
                shuffle(skip_nodes)
                k = randint(1, len(skip_nodes))
                    prod = choice(skip_prods[node.symbol])
                    tree.insert(node, prod)
            else:
                break
    leaves = tree.leaves()
    for node in leaves[:]:
        prod = grammar.symbol_ground(node.symbol)
        tree.insert(node, prod)
    return tree
    