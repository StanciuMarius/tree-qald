import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree
from common.query_tree import SerializationFormat
from services.tasks import run_task, Task
from nltk.tree import Tree
from pptree import print_tree

INTERMEDIATE_QUERY         = r'services\parser\tmp\intermediate_input_query.seq_lu'
MODEL_PATH                 = r'services\parser\tmp\model\ptb-bilstm2-chlstm-glove'
INTERMEDIATE_OUTPUT        = r'services\parser\tmp\intermediate_output.paran'
NCRFPP_PATH                = r'services\parser\tree2labels\NCRFpp'

question = 'How many children does Michael Jackson have?'
question = 'Is Jackson Pollock a painter?'
question = 'Give me all cosmonauts.'

tokens = run_task(Task.TOKENIZE, question)
with open(INTERMEDIATE_QUERY, 'w') as intermediate_output_file:
    intermediate_output_file.write('-BOS-\t-BOS-\t-BOS-\n')
    for token in tokens:
        intermediate_output_file.write(token + '\tTOKEN\tUNUSED\n')
    intermediate_output_file.write('-EOS-\t-EOS-\t-EOS-\n')

parse_command = 'python ./services/parser/tree2labels/run_ncrfpp.py --test {INPUT} --model {MODEL} --status test --gpu False --output {OUTPUT} --ncrfpp {NCRFPP}'
parse_command = parse_command.format(INPUT=INTERMEDIATE_QUERY, MODEL=MODEL_PATH, OUTPUT=INTERMEDIATE_OUTPUT, NCRFPP=NCRFPP_PATH)
os.system(parse_command)


with open(INTERMEDIATE_OUTPUT, 'r') as intermediate_output_file:
    tree_candidates = intermediate_output_file.readlines()

def tree2dict(tree: Tree):
    result = {}

    result['type'] = tree.label()
    children = [tree2dict(t)  if isinstance(t, Tree)  else t for t in tree]
    if tree.label() == 'TOKEN':
        result['index'] = int(children[0])
    elif children:
        result['children'] = children
    
    return result

for tree in tree_candidates:
    tree = tree.strip()
    nltk_tree: Tree = Tree.fromstring(tree, remove_empty_top_bracketing=True)
    dict_tree = tree2dict(nltk_tree)
    dict_tree['tokens'] = tokens
    query_tree = QueryTree.from_dict(dict_tree, tokens)
    print_tree(query_tree.root, childattr='children')
