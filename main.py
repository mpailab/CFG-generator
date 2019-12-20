import argparse
from random import choice, randint, shuffle
from generator import run
from grammar import CFG
from tree import Tree

DEPTH = 150
SIZE = 10000

parser = argparse.ArgumentParser( description='generate an arbitrary string in context-free grammar',
                                  formatter_class=argparse.HelpFormatter)
parser.add_argument( '--file', metavar='path', type=str, help='file with grammar', required=True)
parser.add_argument( '--output', metavar='path', type=str, default='stdout', help='output file (default: %(default)s)')
parser.add_argument( '--depth', metavar='int', type=int, default=DEPTH, help='depth of derivation tree (default: %(default)s)')
parser.add_argument( '--size', metavar='int', type=int, default=SIZE, help='size of derivation tree (default: %(default)s)')
parser.add_argument( '--dynamic', action='store_true', help='save output string in dynamic grammar')
args = parser.parse_args()

with open(args.file, 'r') as file:
    cfg = CFG.fromsource(file)
    tree = run(cfg, args.depth, args.size)
    if args.output == 'stdout':
        print(tree.to_str(not args.dynamic))
    else:
        with open(args.output, 'w') as output:
            output.write(tree.to_str())