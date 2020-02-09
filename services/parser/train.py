from typing import Set
import json
import os
import sys
import random
from pptree import print_tree

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType, SerializationFormat
from services.parser.utils import contains_bad_exists
from services.parser.constants import TRAIN_TEST_RATIO, NCRFPP_TRAIN_CONFIG_FILE_PATH, QUESTION_SET_FILE_PATH, INTERMEDIATE_TEST_FILE_PATH, INTERMEDIATE_TRAIN_FILE_PATH, INTERMEDIATE_OUTPUT_DIRECTORY_PATH, DATASET_NAME
from services.parser.preprocess import transform_split
from services.parser.tree2labels.dataset import _set_tag_for_leaf_unary_chain, write_linearized_trees

# dataset_preprocess_command = 'python services/parser/tree2labels/dataset.py --train {TRAIN} --dev {DEV} --test {TEST} --output {OUTPUT} --treebank {NAME} --encode_unaries --os --abs_top 3 --abs_neg_gap 2'
# dataset_preprocess_command = dataset_preprocess_command.format(TRAIN=INTERMEDIATE_TRAIN_FILE_PATH, TEST=INTERMEDIATE_TEST_FILE_PATH, DEV=INTERMEDIATE_TEST_FILE_PATH, OUTPUT=INTERMEDIATE_OUTPUT_DIRECTORY_PATH, NAME=DATASET_NAME)
# os.system(dataset_preprocess_command)

def prepare_input():
    


    with open(QUESTION_SET_FILE_PATH, 'r', encoding='utf-8') as input_file:
        questions = json.load(input_file)
        questions = list(filter(lambda question: question['root'], questions))
        questions = list(map(lambda question: QueryTree.from_dict(question), questions))
        questions = list(filter(lambda question: not contains_bad_exists(question), questions))
        for question in questions:
            question.remove_children_of_type(NodeType.VARIABLE)
            

        random.shuffle(questions)
        split_point = int(TRAIN_TEST_RATIO * len(questions))

        train_questions = questions[:split_point]
        test_questions = questions[split_point:]


        with open(INTERMEDIATE_TRAIN_FILE_PATH, 'w', encoding='utf-8') as output_file:
            for question in train_questions:
                line = question.to_serializable(SerializationFormat.PREFIX_PARANTHESES) + '|' + ' '.join(question.tokens) + '\n'
                output_file.write(line)

        with open(INTERMEDIATE_TEST_FILE_PATH, 'w', encoding='utf-8') as output_file:
            for question in test_questions:
                line = question.to_serializable(SerializationFormat.PREFIX_PARANTHESES) + '|' + ' '.join(question.tokens) + '\n'
                output_file.write(line)

    args_binarized = False
    args_os = True
    args_root_label = False
    args_encode_unaries = True
    args_abs_top = 3
    args_abs_neg_gap = 2
    args_join_char = '~'
    args_split_char = '@'

    train_sequences, train_leaf_unary_chains = transform_split(INTERMEDIATE_TRAIN_FILE_PATH, args_binarized, args_os, args_root_label, 
                                                         args_encode_unaries, args_abs_top, args_abs_neg_gap,
                                                         args_join_char, args_split_char) 
    
    dev_sequences, dev_leaf_unary_chains = transform_split(INTERMEDIATE_TEST_FILE_PATH, args_binarized, args_os, args_root_label, 
                                                     args_encode_unaries, args_abs_top, args_abs_neg_gap,
                                                     args_join_char, args_split_char) 
    ext = "seq_lu"
    feats_dict = {}
    write_linearized_trees("/".join([INTERMEDIATE_OUTPUT_DIRECTORY_PATH, DATASET_NAME + "-train."+ext]), train_sequences)
    
    write_linearized_trees("/".join([INTERMEDIATE_OUTPUT_DIRECTORY_PATH, DATASET_NAME + "-dev."+ext]), dev_sequences)
              
    test_sequences, test_leaf_unary_chains = transform_split(INTERMEDIATE_TEST_FILE_PATH, args_binarized, args_os, args_root_label, 
                                                     args_encode_unaries, args_abs_top, args_abs_neg_gap,
                                                     args_join_char, args_split_char) 
    
    write_linearized_trees("/".join([INTERMEDIATE_OUTPUT_DIRECTORY_PATH, DATASET_NAME + "-test."+ext]), test_sequences)   



def train():
    prepare_input()
    train_command = 'python services/parser/tree2labels/NCRFpp/main.py --config {CONFIG}'
    train_command = train_command.format(CONFIG=NCRFPP_TRAIN_CONFIG_FILE_PATH)
    os.system(train_command)

train()
