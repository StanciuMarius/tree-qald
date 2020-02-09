import json
import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task

RELATION_NODE_TYPES = {
    NodeType.PROPERTY,
    NodeType.ARGMAXCOUNT,
    NodeType.ARGMINCOUNT,
    NodeType.ARGMAX,
    NodeType.ARGMIN,
    NodeType.ARGNTH,
    NodeType.EXISTSRELATION,
    NodeType.GREATER,
    NodeType.ISGREATER,
    NodeType.ISLESS,
    NodeType.LESS,
    NodeType.SAMPLE,
    NodeType.EQUAL
    NodeType.TOPN
    }
INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'

# def map_relations(tree: QueryTree):

                
#             # candidates = run_task(Task.MAP_RELATION, {})


with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    questions = list(filter(lambda question: question['root'], questions))
    questions = list(map(lambda question: QueryTree.from_dict(question), questions))
    invalid = 0
    
    for tree in questions:
        relation_nodes: List[QueryTree.Node] = tree.root.collect(RELATION_NODE_TYPES)
        for node in relation_nodes:

            if node.type == NodeType.
            subjects = node.collect({NodeType.ENTITY, NodeType.LITERAL, NodeType.TYPE, NodeType.VARIABLE})
            if len(subjects) == 2:
                head, tail = subjects
            if len(subjects) == 1 and len(variables) == 1:
                head, tail = subjects[0], variables[0]
            else:
                print ("Unsupported case for relation mapping.")
                tree.pretty_print()
                invalid += 1    
                continue

    print(str(invalid) + '/' + str(len(questions)))