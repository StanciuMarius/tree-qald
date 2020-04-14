import os
import sys
from typing import List
import json

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task

TREES_TO_CONSIDER = 3
def answer(question_text: str) -> List[str]:
    # Parse the query to obtain a query tree.
    trees = run_task(Task.PARSE, question_text)
    first_mapped_tree = None
    
    for tree in trees[:TREES_TO_CONSIDER]:
        QueryTree.from_dict(tree).pretty_print()
        query = run_task(Task.GENERATE_QUERY, tree)
        if not first_mapped_tree: first_mapped_tree = query['tree']
        QueryTree.from_dict(query['tree']).pretty_print()
        
        if not query or not query['query_body']: continue

        answer = run_task(Task.RUN_SPARQL_QUERY, query)
        if answer or type(answer) == bool:
            return answer, query['query_body'], query['tree']
        else:
            print("No answer, trying next tree...")
    
    return None, None, first_mapped_tree
