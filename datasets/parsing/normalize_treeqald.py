import json
import os
import sys
sys.path.insert(0, os.getcwd())

from common.constants import GRAMMAR_FILE_PATH
from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from common.syntax_checker import SyntaxChecker

SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)

def normalize_treeqald(source_path):
    '''
    Convert a tree-annotated question dataset to a relation extraction dataset (from its relation nodes)
    '''

    file_name = os.path.basename(source_path)
    file_name = file_name.split('.')[0]
    output_path = os.path.join(r'datasets\relation_extraction\tree-qald\data', file_name + '_normalized.json')
    if os.path.exists(output_path): return output_path

    with open(source_path, 'r', encoding='utf-8') as input_file:
        trees = json.load(input_file)
        trees = [question for question in trees if 'root' in question and question['root']]
        trees = list(map(lambda question: QueryTree.from_dict(question), trees))
        trees = list(filter(lambda x: SYNTAX_CHECKER.validate(x), trees))
    
    sequences = []
    for tree in trees:
        relation_nodes = tree.root.collect(RELATION_NODE_TYPES)
        for node in relation_nodes:
            if node.kb_resources:
                sequences.append(tree.generate_relation_extraction_sequence(node))
        
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(sequences, output_file)

    return output_path


