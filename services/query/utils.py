import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task

def index_to_offset(token_indexes: List[int], tokens: List[str]) -> (int, int):
    '''
        Convertor from token index clusters to begin-end offset notation.
        E.g. Who is the wife of Barack Obama?
        input: [0]
        output: (0,3)
    '''
    token_indexes = sorted(token_indexes)
    text = ' '.join(tokens)

    target_text  = ' '.join([tokens[token] for token in token_indexes])
    target_begin = text.find(target_text)
    target_end    = target_begin + len(target_text)

    return (target_begin, target_end)

def offset_for_node(node: QueryTree.Node, tokens: List[str]):
    tokens = [token.id for token in node.collect({NodeType.TOKEN})]
    begin_offset, end_offset = index_to_offset(tokens, tree.tokens)

    return begin_offset, end_offset

def map_relations(tree: QueryTree):
    relation_nodes: List[QueryTree.Node] = tree.root.collect({NodeType.PROPERTY, NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.EXISTSRELATION, NodeType.GREATER, NodeType.ISGREATER, NodeType.ISLESS, NodeType.LESS})


    for node in relation_nodes:
        variables = list(filter(lambda child: child.type == NodeType.VARIABLE, tree.root.children))

        # Binary queries (subject-object children)
        if node.type in {NodeType.PROPERTY, NodeType.EXISTSRELATION, NodeType.ISGREATER, NodeType.ISLESS}:
            subjects = node.collect({NodeType.ENTITY, NodeType.LITERAL, NodeType.TYPE, NodeType.VARIABLE})
            if len(subjects) == 2:
                head, tail = subjects
            if len(subjects) == 1 and len(variables) == 1:
                head, tail = subjects[0], variables[0]
            else:
                print ("Unsupported case for relation mapping.")
                continue
            
            candidates = run_task(Task.MAP_RELATION, {})
