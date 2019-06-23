from typing import Set
import json
import os
import sys
import random
from pptree import print_tree

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType, SerializationFormat
from services.parser.utils import contains_bad_exists
from services.parser.constants import TRAIN_TEST_RATIO, INPUT_ANNOTATED_QUESTIONS, INTERMEDIATE_TEST_FILE, INTERMEDIATE_TRAIN_FILE, INTERMEDIATE_OUTPUT_FILE, DATASET_NAME



with open(INPUT_ANNOTATED_QUESTIONS, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    questions = list(filter(lambda question: question['tree'], questions))
    questions = list(map(lambda question: QueryTree.from_dict(question['tree'], question['tokens']), questions))
    questions = list(filter(lambda question: not contains_bad_exists(question), questions))

random.shuffle(questions)
split_point = int(TRAIN_TEST_RATIO * len(questions))

train_questions = questions[:split_point]
test_questions = questions[split_point:]

with open(INTERMEDIATE_TRAIN_FILE, 'w', encoding='utf-8') as output_file:
    for question in train_questions:
        line = question.to_serializable(SerializationFormat.PREFIX_PARANTHESES) + '|' + ' '.join(question.tokens) + '\n'
        output_file.write(line)

with open(INTERMEDIATE_TEST_FILE, 'w', encoding='utf-8') as output_file:
    for question in test_questions:
        line = question.to_serializable(SerializationFormat.PREFIX_PARANTHESES) + '|' + ' '.join(question.tokens) + '\n'
        output_file.write(line)

dataset_preprocess_command = 'python services/parser/tree2labels/dataset.py --train {TRAIN} --dev {DEV} --test {TEST} --output {OUTPUT} --treebank {NAME} --encode_unaries --os --abs_top 3 --abs_neg_gap 2'
dataset_preprocess_command = dataset_preprocess_command.format(TRAIN=INTERMEDIATE_TRAIN, TEST=INTERMEDIATE_TEST, DEV=INTERMEDIATE_TEST, OUTPUT=INTERMEDIATE_OUTPUT_FILE, NAME=DATASET_NAME)
os.system(dataset_preprocess_command)

train_command = 'python services/parser/tree2labels/NCRFpp/main.py --config {CONFIG}'
train_command = train_command.format(CONFIG=MODEL_CONFIG_FILE)
os.system(train_command)
