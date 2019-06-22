from typing import Set
import json
import os
import sys

from pptree import print_tree
sys.path.insert(0, os.getcwd())
from annotator.constants import INPUT_FILE_PATH, OUTPUT_FILE_PATH
from common.query_tree import QueryTree, NodeType, SerializationFormat


INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'
OUTPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.prefix'


def contains_any(question: QueryTree, target: Set[NodeType]):
    def contains_node_in_set_recursive(node: QueryTree.Node, target: Set[NodeType]):
        if node.type in target:
            return True
        else:
            for child in node.children:
                if contains_node_in_set_recursive(child, target):
                    return True
        
        return False

    return contains_node_in_set_recursive(question.root, target)

def contains_bad_exists(question: QueryTree):
    def containts_bad_exists_recursive(node: QueryTree.Node):
        if node.type == NodeType.PROPERTY and len(node.children) == 2 and node.children[0].type == NodeType.ENTITY and node.children[1].type == NodeType.ENTITY:
            return True
        else:
            for child in node.children:
                if containts_bad_exists_recursive(child):
                    return True
        
        return False

    return containts_bad_exists_recursive(question.root)

with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    questions = list(filter(lambda question: question['tree'], questions))
    questions = list(map(lambda question: QueryTree.from_dict(question['tree'], question['tokens']), questions))
    questions = list(filter(lambda question: not contains_bad_exists(question), questions))
    print(len(questions))

with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
    for question in questions:
        line = question.to_serializable(SerializationFormat.PREFIX_PARANTHESES) + '|' + ' '.join(question.tokens) + '\n'
        output_file.write(line)
        # print_tree(question.root, childattr='children')



