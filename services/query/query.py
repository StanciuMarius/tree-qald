import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task
from services.query.utils import map_relations

def answer(question_text: str) -> List[str]:
    
    # Parse the query to obtain a query tree. TODO consider more candidates (atm [0])
    tree_dicts = run_task(Task.PARSE, question_text)
    trees = list(map(lambda tree_dict: QueryTree.from_dict(tree_dict), tree_dicts))
    for tree in trees:
        # Map the entities
        entities: List[QueryTree.Node] = tree.root.collect({NodeType.ENTITY})
        for entity in entities:
            entity_begin, entity_end = tree.offset_for_node(entity)
            entity.kb_resources = run_task(Task.MAP_ENTITY, {'text': question_text, 'entity_begin': entity_begin, 'entity_end': entity_end })

        # Map the types
        types: List[QueryTree.Node] = tree.root.collect({NodeType.TYPE})
        for type in types:
            type_begin, type_end = tree.offset_for_node(type)
            type.kb_resources = run_task(Task.MAP_TYPE, {'text': question_text, 'type_begin': type_begin, 'type_end': type_end })
        tree.pretty_print()

        # Map the relations
        map_relations(tree)


answer("Who is the oldest child of Barack Obama?")
