from typing import Set
import json
import os
import sys
from random import shuffle
from pptree import print_tree
sys.path.insert(0, os.getcwd())
from annotator.constants import INPUT_FILE_PATH, OUTPUT_FILE_PATH
from common.query_tree import QueryTree, NodeType, SerializationFormat
from common.syntax_checker import SyntaxChecker
from common.constants import GRAMMAR_FILE_PATH

SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)

INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'

def filter_predicate(question: QueryTree):
    return SYNTAX_CHECKER.validate(question)

with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    questions = list(map(lambda question: QueryTree.from_dict(question), questions))
    filtered_questions = list(filter(filter_predicate, questions))
    print('{}/{} passed the filter_predicate!'.format(len(filtered_questions), len(questions)))

