# Generating Sentences from Context-Free Grammars

### Tool usage

    main.py [-h] [--output path] [--depth int] [--size int] [--dynamic] [--sep str] file

    positional arguments:
    file           file with grammar

    optional arguments:
    -h, --help     show this help message and exit
    --output path  output file (default: stdout)
    --depth int    depth of derivation tree (default: 150)
    --size int     size of derivation tree (default: 10000)
    --dynamic      save output string in dynamic grammar
    --sep str      derivation symbol in productions (default: =)

### Context-free grammar format

1. Terminal symbols have the form:

        <term> = '[^']+' or "[^"]+"
   
2. Nonterminal symbols have the form:

        <nonterm> = [\w/][\w/^<>-]*

3. Production have the form:

        <production> = <nonterm> <sep> <altsyms>, where <altsyms> = <syms> or <syms> <alt> <altsyms>
                                                        <syms>    = <sym> or <sym> <syms>
                                                        <sym>     = <term> or <nonterm>
                                                        <alt>     = |
                                                        <sep> is defined by --sep

4. Multiline productions separeted by \ are allowed.

5. Lines started with # are connents, with % are directives.

6. There are four directives  
- set the start symbol of grammar:  

        % start <nonterm> 

- set the indent token of grammar:

        % indent <nonterm> 

- set the dedent token of grammar:

        % dedent <nonterm> 
        
- set symbols such that additional productions can be inserted in derivation tree before subtrees corresponding these symbols:  

        % syntax <nonterm> ... <nonterm>
        
- set a production that are not taken into account when calculating the depth of derivation tree:  

        % skip  
        <production>
        
- set an additional production that can be inserted in derivation tree:  

        % add  
        <production>

Directives 'syntax' and 'add' are considered only for dynamic grammars mode. This mode can be turned on by --dynamic.

### An example of context-free grammar

    % start S
    % syntax S
    S = C
    % skip
    S = C '\n' S               # this production is skipped in calculating the depth of derivation tree
    C = V '=' E
    V = 'x' | 'y' | 'z'
    E = V \
      | '(' E '+' E ')' \
      | E '*' E \
      | 'a'
    % add
    E = '(' E '-' E ')'  | 'b' # this production is marked as addition in dynamic grammars
    % add
    V = 'u'                    # and this is also
    
### An example of output file

    x = ( a * a + a * a )
    %syntax: E = ( E - E )
    y = ( a * ( x - a ) + a )
    %syntax: E = b
    z = ( z + b )
