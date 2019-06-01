import os
import sys
import json
import copy
from typing import List

sys.path.insert(0, os.getcwd())
from services.tasks import run_task, Task
from annotator.constants import INPUT_FILE_PATH, OUTPUT_FILE_PATH
from common.query_tree import QueryTree, NodeType, SerializationFormat, enum_for_str


questions = [line.split('|') for line in open(INPUT_FILE_PATH, 'r', encoding='utf-8').readlines()]
trees = json.load(open(OUTPUT_FILE_PATH, 'r', encoding='utf-8'))


def tokens_to_token(tree_dict: dict):
    children = tree_dict['children']
    children_copy = copy.copy(children)

    for child in children_copy:
        if child['type'] == 'TOKENS':
            children.remove(child)
            for token in child['tokens']:
                children.append({
                    'type': 'TOKEN',
                    'index': token
                })
        else:
            tokens_to_token(child)

def from_dict(tree_dict: dict, tokens: List[str]):
    token_nodes = [QueryTree.Node(NodeType.TOKEN, id) for id in range(len(tokens))]
    used_nodes = set()
    
    def node_from_dict(tree_dict):
        node_type = enum_for_str(tree_dict['type'])

        if node_type == NodeType.TOKEN:
            node = token_nodes[tree_dict['index']]
            used_nodes.add(node)
        else:
            node = QueryTree.Node(node_type)

        if 'children' in tree_dict:
            for child in tree_dict['children']:
                node.children.append(node_from_dict(child))
        
        return node

    root = node_from_dict(tree_dict['tree'])

    # Aggregate unused tokens 
    if len(used_nodes) < len(token_nodes):
        unused_container_node = QueryTree.Node(NodeType.UNUSED)
        root.children.append(unused_container_node)

        for node in token_nodes:
            if node not in used_nodes:
                unused_container_node.children.append(node)
    
        
    tree = QueryTree(root, tokens)
    return tree

with open('jimmy.ask', 'w') as output_file:
    for tree in trees:
        try:
            index = int(tree['index'])
            tokens = run_task(Task.TOKENIZE, questions[index][1])
            tokens_to_token(tree['tree'])
            query_tree = from_dict(tree, tokens)
            output_file.write(query_tree.to_serializable(SerializationFormat.PREFIX_PARANTHESES))
        except:
            print("failed!")

