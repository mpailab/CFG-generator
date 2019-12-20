import re

class Symbol (object):

    _dict = dict()

    def __new__ (cls, symbol):
        assert ( isinstance(symbol, str) )
        if symbol in Symbol._dict:
            return Symbol._dict[symbol]
        else:
            return super(Symbol, cls).__new__(cls)

    def __init__ (self, symbol):
        assert ( isinstance(symbol, str) )
        if symbol not in Symbol._dict:
            self._symbol = symbol
            self._syntax = False
            self._skip = False
            self._terminal = False
            Symbol._dict[symbol] = self

    def __eq__ (self, other):
        return self._symbol == other._symbol

    def __ne__ (self, other):
        return not self._symbol == other._symbol
    
    def __str__ (self):
        return self._symbol
    
    def __hash__ (self):
        return hash(self._symbol)

    def syntax (self):
        self._syntax = True

    def is_syntax (self):
        return self._syntax

    def skip (self, skip):
        self._skip = skip

    def is_skip (self):
        return self._skip

    def is_terminal (self):
        return self._terminal

class Terminal (Symbol):

    def __init__ (self, symbol):
        assert ( isinstance(symbol, str) )
        self._symbol = symbol
        self._syntax = False
        self._skip = False
        self._terminal = True

class Production (object):

    def __init__ (self, lhs, rhs, add = False, skip = False, deriv_symbol = '->'):

        assert ( isinstance(lhs, Symbol) and not lhs.is_terminal() and
                 isinstance(rhs, list) and all (isinstance(x, Symbol) for x in rhs) and
                 isinstance(add, bool) and isinstance(skip, bool) and
                 isinstance(deriv_symbol, str) )

        self._lhs = lhs
        self._rhs = rhs
        self._add = add
        self._skip = skip
        self._deriv_symbol = deriv_symbol
    
    def __str__ (self):
        return str(self._lhs) + ' ' + self._deriv_symbol + ' ' + ' '.join(map(str,self._rhs))
    
    def __hash__ (self):
        return hash((self._lhs, tuple(self._rhs)))

    def lhs (self):
        return self._lhs

    def rhs (self):
        return self._rhs

    def is_add (self):
        return self._add

    def is_skip (self):
        return self._skip

    def is_ground (self):
        return all (x.is_terminal() for x in self._rhs)

    def to_pair (self):
        return (self._lhs, self._rhs)

    # Apply a substitution of the form { nonterminal -> rhs }
    def subst (self, f):
        rhs = [ x for y in self._rhs for x in (f[y] if y in f else [y]) ]
        return Production(self._lhs, rhs, deriv_symbol = self._deriv_symbol)

def _ground_subst (prods):
    map_to_ground = {}
    if prods:
        map_to_ground = dict([ x.to_pair() for x in prods if x.is_ground() ])
        prods = [ x.subst(map_to_ground) for x in prods if not x.is_ground() ]
        map_to_ground.update(_ground_subst(prods))
    return map_to_ground

# Class of context-free grammars
class CFG (object):

    def __init__ ( self,             # grammar
                   start,            # start symbol
                   prods_list,       # list of productions
                   prods_map = None, # hash of productions { symbol -> list of productions }
                   deriv_symbol = '->'): # derivation symbol

        assert ( isinstance(start, Symbol) and not start.is_terminal() and
                 isinstance(prods_list, list) and 
                 all ( isinstance(x, Production) for x in prods_list ) and
                 isinstance(prods_map, dict) and 
                 all ( ( isinstance(s, Symbol) and not s.is_terminal() and
                         isinstance(l, list) and 
                         all ( isinstance(x, Production) and s == x.lhs() for x in l ) ) 
                       for s, l in prods_map.items() ) )

        self._start = start
        self._prods_list = prods_list
        self._prods_map = prods_map
        if self._prods_map is None:
            self._prods_map = {}
            for prod in prods_list:
                s = prod.lhs()
                if s in self._prods_map:
                    self._prods_map[s].append(prod)
                else:
                    self._prods_map[s] = [prod]
        self._ground_prods = {}
        for lhs, rhs in _ground_subst(prods_list).items():
            self._ground_prods[lhs] = Production(lhs, rhs, deriv_symbol = deriv_symbol)

    def start (self):
        return self._start

    def prods (self):
        return self._prods_list

    def skip_prods (self):
        return { k : [ x for x in v if x.is_skip() ] for k, v in self._prods_map.items() if k.is_skip() }

    def symbol_prods (self, symbol):
        assert ( isinstance(symbol, Symbol) and not symbol.is_terminal() )
        return self._prods_map[symbol]

    def symbol_ground (self, symbol):
        assert ( isinstance(symbol, Symbol) and not symbol.is_terminal() )
        return self._ground_prods[symbol]
    
    @classmethod
    def fromsource(cls, source, deriv_symbol = '->'):
        assert ( ( isinstance(source, str) or hasattr(source, 'read') ) and 
                 isinstance(deriv_symbol, str) )
        start, prods_list, prods_map = _parse_grammar(source, deriv_symbol)
        return cls(start, prods_list, prods_map, deriv_symbol)

def _parse_nonterminal (string, pos):
    m = re.compile(r'\s*([\w/][\w/^<>-]*)\s*').match(string, pos)
    if not m:
        raise ValueError('Expected a nonterminal, found: ' + string[pos:])
    return (Symbol(m.group(1)), m.end())

def _parse_production (string, deriv_symbol, is_add, is_skip):

    # Parse the left-hand side
    lhs, pos = _parse_nonterminal(string, 0)

    # Skip over the derivation symbol
    m = re.compile(r'\s*%s\s*' % deriv_symbol).match(string, pos)
    if not m:
        raise ValueError('Expected the derivation symbol %r, found: %s' % (deriv_symbol, string[pos:]))
    pos = m.end()

    # Parse the right hand side
    rhsides = [[]]
    while pos < len(string):

        # String -- add terminal
        if string[pos] in "\'\"":
            m = re.compile(r'(\"[^\"]+\"|\'[^\']+\')\s*').match(string, pos)
            if not m:
                raise ValueError('Expected a terminal, found: ' + string[pos:])
            rhsides[-1].append(Terminal(m.group(1)[1:-1]))
            pos = m.end()

        # Separating symbol -- start new rhside
        elif string[pos] == '|':
            m = re.compile(r'\s*\|\s*').match(string, pos)
            if not m:
                raise ValueError('Expected the separating symbol |, found: ' + string[pos:])
            rhsides.append([])
            pos = m.end()

        # Anything else -- add nonterminal
        else:
            nonterm, pos = _parse_nonterminal(string, pos)
            rhsides[-1].append(nonterm)
            
    return (lhs, [Production(lhs, rhs, is_add, is_skip, deriv_symbol) for rhs in rhsides])

def _parse_grammar (source, deriv_symbol = '->'):
    
    start = None
    prods_list = []
    prods_map = {}
    is_add_prod = False
    is_skip_prod = False

    continue_line = ''
    lines = source.split('\n') if isinstance(source, str) else source
    for linenum, line in enumerate(lines):

        # Concatenate multiple lines of single string
        line = continue_line + line.strip()
        if line.endswith('\\'):
            continue_line = line[:-1].rstrip() + ' '
            continue
        continue_line = ''

        # Skip comments
        if line.startswith('#') or line == '':
            continue

        try:
            # Parse grammar directive
            if line[0] == '%': 

                directive = line[1:].split(None, 1)
                if directive[0] == 'start':
                    if start is not None:
                        raise ValueError('Second occurrence of start directive')
                    start, pos = _parse_nonterminal(directive[1], 0)
                    if pos != len(directive[1]):
                        raise ValueError('Bad argument to start directive')

                elif directive[0] == 'syntax':
                    pos = 0
                    while pos != len(directive[1]):
                        syntax_symbol, pos = _parse_nonterminal(directive[1], pos)
                        syntax_symbol.syntax()

                elif directive[0] == 'add':
                    if len(directive) > 1:
                        raise ValueError('Unexpected argument to add productions directive')
                    is_add_prod = True

                elif directive[0] == 'skip':
                    if len(directive) > 1:
                        raise ValueError('Unexpected argument to skip productions directive')
                    is_skip_prod = True

            # Parse gramma production
            else:

                lhs, prods = _parse_production(line, deriv_symbol, is_add_prod, is_skip_prod)
                lhs.skip(is_skip_prod)
                prods_list += prods
                if lhs in prods_map:
                    prods_map[lhs] += prods
                else:
                    prods_map[lhs] = prods

                is_add_prod = False
                is_skip_prod = False
        
        except ValueError as e:
            raise ValueError('Unable to parse line %s: %s\n%s' % (linenum + 1, line, e))

    if not prods_list:
        raise ValueError('No productions found!')

    return (start, prods_list, prods_map)