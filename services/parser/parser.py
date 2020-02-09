from typing import List

import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree
from common.query_tree import SerializationFormat
from common.constants import GRAMMAR_FILE_PATH
from common.syntax_checker import SyntaxChecker

from services.tasks import run_task, Task
from nltk.tree import Tree
from pptree import print_tree
from typing import List

from services.parser.constants import INTERMEDIATE_QUERY_FILE_PATH, MODEL_FILE_PATH, FINAL_OUTPUT_FILE_PATH, NCRFPP_REPOSITORY_PATH, NCRFPP_DECODE_CONFIG_FILE_PATH, TREE_CANDIDATES_N_BEST
from services.parser.tree2labels.utils import sequence_to_parenthesis, get_enriched_labels_for_retagger
from services.parser.preprocess import postprocess_labels
SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)


def parse(query_text: str) -> List[dict]:
    '''
    Parses the input query text as a set of candidate constituency trees
    '''
    tokens = run_task(Task.TOKENIZE, query_text)
    _prepare_input(tokens)
    _run_ncrfpp()
    candidates = _decode_labels(tokens)

    # Statistically parsed trees might not validate the grammar. Discard invalid trees
    candidates = list(filter(lambda tree: SYNTAX_CHECKER.validate(tree), candidates))
    candidates = list(map(lambda tree: tree.to_serializable(SerializationFormat.HIERARCHICAL_DICT), candidates))
    #print('Produced {}/{} valid candidates!'.format(len(candidates), TREE_CANDIDATES_N_BEST))
    
    return candidates

def _prepare_input(tokens):
    '''
    Create an input file for the NCRFPP library. It contains the query to be tagged.
    '''
    with open(INTERMEDIATE_QUERY_FILE_PATH, 'w') as intermediate_output_file:
        intermediate_output_file.write('-BOS-\t-BOS-\t-BOS-\n')
        for token in tokens:
            intermediate_output_file.write(token + '\tTOKEN\tUNUSED\n')
        intermediate_output_file.write('-EOS-\t-EOS-\t-EOS-\n')

def _run_ncrfpp():
    '''
    Run the NCRFPP algorithm on the input files
    '''
    # Write input of ncrfpp in a configuration file
    config_string =  "### Decode ###\nstatus=decode\n"
    config_string += "raw_dir=" + INTERMEDIATE_QUERY_FILE_PATH + "\n"
    config_string += "decode_dir=" + MODEL_FILE_PATH + ".output" + "\n"
    config_string += "dset_dir=" + MODEL_FILE_PATH + ".dset" + "\n"
    config_string += "load_model_dir=" + MODEL_FILE_PATH + ".model" + "\n"
    config_string += "gpu=False\n"
    config_string += "nbest=" + str(TREE_CANDIDATES_N_BEST) + "\n"

    with open(NCRFPP_DECODE_CONFIG_FILE_PATH, "w", encoding="utf-8") as decode_config_file:
        decode_config_file.write(config_string)

    ncrfpp_command_string = "python " + NCRFPP_REPOSITORY_PATH + "/main.py --config " + NCRFPP_DECODE_CONFIG_FILE_PATH
    os.system(ncrfpp_command_string)

def _decode_labels(tokens):
    '''
    Process the output of the NCRFPP algorithm.
    '''
    parenthesized_trees = []
    with open(MODEL_FILE_PATH + ".output", encoding="utf-8") as ncrfpp_output_file:
        lines = ncrfpp_output_file.readlines()
        lines = [line.strip().split(' ') for line in lines[1:]]
        for prediction_index in range(0, TREE_CANDIDATES_N_BEST):
            try:
                sentence = []
                pred = []
                for token_index, line_tokens in enumerate(lines):
                    # The tree2labels algorithm is not aware of 'UNUSED' tokens. We first have to eliminate them, so the sequence_to_parenthesis algorithm
                    # reconstructs the tree corectly
                    if len(line_tokens) >= 2 and 'UNUSED' != line_tokens[1]:
                        sentence.append((str(token_index - 1), 'TOKEN')) # -1 because of the -BOS- line
                        pred.append(line_tokens[1 + prediction_index])

                # The main decoding process of tree2labels repo
                parenthesized_trees.extend(sequence_to_parenthesis([sentence], [pred]))
            except:
                print("Error decoding tree")

    candidates = []

    for tree in parenthesized_trees:
        def tree2dict(tree: Tree):
            result = {}

            result['type'] = tree.label()
            children = [tree2dict(t)  if isinstance(t, Tree)  else t for t in tree]
            if tree.label() == 'TOKEN':
                result['id'] = int(children[0])
            elif children:
                result['children'] = children

            return result

        tree = tree.strip()
        nltk_tree: Tree = Tree.fromstring(tree, remove_empty_top_bracketing=True)
        dict_tree = {
            'root':  tree2dict(nltk_tree),
            'tokens': tokens   
        }
        query_tree = QueryTree.from_dict(dict_tree)
        candidates.append(query_tree)

    return candidates



# candidates = parse("What is the largest city in Brazil?")
# best = candidates[0]
# print(best['tokens'])
