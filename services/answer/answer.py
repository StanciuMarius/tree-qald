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
        if not query: continue

        answer = run_task(Task.RUN_SPARQL_QUERY, query)
        if answer: return query['query_body'], answer
    
    raise Exception("Could not generate answer")

# query_body, result = answer("Who is the oldest actor that plays in a movie directed by Quentin Tarantino?") # good
# query_body, result = answer("Who is the youngest actor that plays in a movie directed by Steven Spielberg?")
# query_body, result = answer("What is the largest country the Danube flows through?") #good
# query_body, result = answer("What is the longest river that flows through Romania?") #good
# query_body, result = answer("Give me the 5 largest mountains in Romania.") #good
# query_body, result = answer("Give me the fifth highest mountain in Romania.") #good
# query_body, result = answer("How old are Barack Obama's children?") #bad
# query_body, result = answer("Who is the youngest child fo Barack Obama?") #bad
query_body, result = answer("Who developed the iPhone?") #bad

print(query_body)
print(result)
