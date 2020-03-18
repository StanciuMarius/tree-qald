import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task
# from services.answer.utils import map_relations

TREES_TO_CONSIDER = 3
def answer(question_text: str) -> List[str]:
    # Parse the query to obtain a query tree.
    trees = run_task(Task.PARSE, question_text)
    
    for tree in trees[:TREES_TO_CONSIDER]:
        query_tree = QueryTree.from_dict(tree)
        query_tree.pretty_print()

        query = run_task(Task.GENERATE_QUERY, tree)
        answer = run_task(Task.RUN_SPARQL_QUERY, query)
        if answer:
            return query['query'], answer
    
    raise "Could not generate answer"

result = answer("Who is the oldest actor that stars in a movie directed by Quentin Tarantino?")
print(result)
