import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree
from common.query_tree import SerializationFormat
from services.tasks import run_task, Task
from nltk.tree import Tree
from pptree import print_tree

from services.parser.constants import INTERMEDIATE_QUERY_FILE_PATH, MODEL_FILE_PATH, FINAL_OUTPUT_FILE_PATH, NCRFPP_REPOSITORY_PATH

def parse(question_text: str) -> dict:
    tokens = run_task(Task.TOKENIZE, question_text)
    with open(INTERMEDIATE_QUERY_FILE_PATH, 'w') as intermediate_output_file:
        intermediate_output_file.write('-BOS-\t-BOS-\t-BOS-\n')
        for token in tokens:
            intermediate_output_file.write(token + '\tTOKEN\tUNUSED\n')
        intermediate_output_file.write('-EOS-\t-EOS-\t-EOS-\n')

    parse_command = 'python ./services/parser/tree2labels/run_ncrfpp.py --test {INPUT} --model {MODEL} --status test --gpu False --output {OUTPUT} --ncrfpp {NCRFPP}'
    parse_command = parse_command.format(INPUT=INTERMEDIATE_QUERY_FILE_PATH, MODEL=MODEL_FILE_PATH, OUTPUT=FINAL_OUTPUT_FILE_PATH, NCRFPP=NCRFPP_REPOSITORY_PATH)
    os.system(parse_command)

    with open(FINAL_OUTPUT_FILE_PATH, 'r') as intermediate_output_file:
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

    candidates = []
    for tree in tree_candidates:
        tree = tree.strip()
        nltk_tree: Tree = Tree.fromstring(tree, remove_empty_top_bracketing=True)
        dict_tree = tree2dict(nltk_tree)
        dict_tree['tokens'] = tokens
        # query_tree = QueryTree.from_dict(dict_tree, tokens)
        candidates.append(dict_tree)
    
    return candidates

# trees = parse("How many children does Barack Obama have?")
# query_tree = QueryTree.from_dict(trees[0], trees[0]['tokens'])
# print_tree(query_tree.root)