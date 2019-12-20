import re
from functools import reduce
from grammar import Symbol, Production

class Node (object):

    def __init__ (self, symbol, parent = None, depth = 0):

        assert ( isinstance(symbol, Symbol) and 
                 ( parent is None or isinstance(parent, Node) ) and
                 isinstance(depth, int) )

        self._symbol = symbol
        self._parent = parent
        self._childs = []
        self._depth = depth
        self._production = None

    def is_root (self):
        return self._parent is None

    def symbol (self):
        return self._symbol

    def parent (self):
        return self._parent

    def childs (self, childs = None):
        if childs is None:
            return self._childs
        assert ( isinstance(childs, list) and all ( isinstance(x, Node) for x in childs ) )
        self._childs = childs

    def depth (self):
        return self._depth

    def production (self, prod = None):
        if prod is None:
            return self._production
        assert ( isinstance(prod, Production) )
        self._production = prod

    def __str__ (self, pref='', next_pref=''):
        res = pref + ('' if next_pref == '' else '+-') + str(self._symbol) + '\n'
        for i, child in enumerate(self._childs):
            res += child.__str__(pref + next_pref, '| ' if i+1 < len(self._childs) else '  ')
        return res

    def terminals (self):
        nodes = [self]
        while any (x.childs() for x in nodes):
            nodes = [ y for x in nodes for y in (x.childs() if x.childs() else [x]) ]
        return nodes
    
    def _to_str (self):
        nodes = self.terminals()
        prod = self._production
        if prod is None:
            return (str(self._symbol), {})

        else:
            assert (self._childs)
            childs_res = list(zip(*map(lambda x: x._to_str(), self._childs)))
            string = ' '.join(childs_res[0])
            prods = { k : v for d in childs_res[1] for k, v in d.items()}
            if prod.is_add():
                prods[prod] = 1

        if (self._symbol.is_syntax() or self._parent is None) and prods:
            string = ''.join(map(lambda x: '%syntax: ' + str(x) + '\n', prods.keys())) + string
            prods = {}

        return (string, prods)
    
    def to_str (self, simple = False):
        if simple:
            string = ' '.join(list(map(lambda x: str(x.symbol()), self.terminals())))
        else:
            string, prods = self._to_str()
            assert (not prods)
        return re.sub(r'\s*\\n\s*', '\n', string)

class Tree (object):

    def __init__ (self, symbol):

        assert ( isinstance(symbol, Symbol) )

        self._root = Node(symbol)
        self._skips = [self._root] if symbol.is_skip() else []
        self._leaves = [] if symbol.is_terminal() else [self._root]
        self._size = 1

    def root (self):
        return self._root

    def skips (self):
        return self._skips

    def leaves (self, depth = None):
        if depth is None:
            return self._leaves
        assert ( isinstance(depth, int) )
        return [ x for x in self._leaves if x.depth() < depth ]

    def size (self):
        return self._size

    def insert (self, node, prod):

        assert ( isinstance(node, Node) and not node.symbol().is_terminal() and
                 isinstance(prod, Production) and node.symbol() == prod.lhs() )

        depth = node.depth() if prod.is_skip() else node.depth() + 1
        childs = [ Node(x, node, depth) for x in prod.rhs() ]

        if node.symbol() in prod.rhs() and node.production() is not None:
            i = prod.rhs().index(node.symbol())
            child = childs[i]
            child.childs(node.childs())
            child.production(node.production())
            self._leaves += [ x for x in childs if not x.symbol().is_terminal() and x != child ]
        else:
            assert (node in self._leaves)
            self._leaves.remove(node)
            self._leaves += [ x for x in childs if not x.symbol().is_terminal() ]
            
        node.childs(childs)
        node.production(prod)
        self._skips += [ x for x in childs if x.symbol().is_skip() ]
        self._size += len(childs)

    def __str__ (self):
        return str(self._root)
    
    def to_str (self, simple = False):
        return self._root.to_str(simple)
