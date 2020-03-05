from typing import Set
from tqdm import tqdm
import json
import os
import sys
from random import shuffle
from pptree import print_tree
sys.path.insert(0, os.getcwd())
from annotator.constants import INPUT_FILE_PATH, OUTPUT_FILE_PATH
from common.query_tree import QueryTree, NodeType, SerializationFormat, RELATION_NODE_TYPES, ENTITY_SET_TYPES
from common.syntax_checker import SyntaxChecker
from common.constants import GRAMMAR_FILE_PATH
from services.mapping.relation_mapping.relation_mapping import generate_relation_extraction_sequences

SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)

INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'
OUTPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions_modified.json'

def filter_predicate(question: QueryTree):
    def validates_grammar(question: QueryTree):
        return SYNTAX_CHECKER.validate(question)
    
    def relations_fully_mapped(question: QueryTree):
        relation_nodes = question.root.collect(RELATION_NODE_TYPES)
        for node in relation_nodes:
            if len(node.kb_resources) == 0:
                return False
        return True
    
    def more_than_n_relations(question: QueryTree, n = 2):
        relation_nodes = question.root.collect(RELATION_NODE_TYPES)
        return len(relation_nodes) > n
    

    def contain_bad_property(question: QueryTree):
        property_nodes = question.root.collect({NodeType.PROPERTY})
        for node in property_nodes:
            entities = list(filter(lambda x: x.type == NodeType.ENTITY, node.children))
            entity_set = list(filter(lambda x: x.type != NodeType.ENTITY and x.type in ENTITY_SET_TYPES, node.children))
            if len(entities) > 0 and len(entity_set) > 0:
                return True
        return False

    return validates_grammar(question)

with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    questions = [question for question in questions if 'root' in question and question['root']]
    questions = list(map(lambda question: QueryTree.from_dict(question), questions))
    filtered_questions = list(filter(filter_predicate, questions))
    print('{}/{} passed the filter_predicate!'.format(len(filtered_questions), len(questions)))


with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
    questions = [question.to_serializable(SerializationFormat.HIERARCHICAL_DICT) for question in filtered_questions]
    json.dump(questions, output_file)











