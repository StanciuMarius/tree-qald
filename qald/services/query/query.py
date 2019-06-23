import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.tasks import Task, run_task
from services.query.utils import index_to_offset, map_relations

def answer(question_text: str) -> List[str]:
    
    # Parse the query to obtain a query tree. TODO consider more candidates (atm [0])
    tree_dict = run_task(Task.PARSE, question_text)[0]
    tree = QueryTree.from_dict(tree_dict, tree_dict['tokens'])
    tree.pretty_print()

    # Map the entities
    entities: List[QueryTree.Node] = tree.root.collect({NodeType.ENTITY})
    for entity in entities:
        entity_begin, entity_end = offset_for_node(entity, tree.tokens)
        entity.kb_resources = run_task(Task.MAP_ENTITY, {'text': question_text, 'entity_begin': entity_begin, 'entity_end': entity_end })

    # Map the types
    types: List[QueryTree.Node] = tree.root.collect({NodeType.TYPE})
    for type in types:
        type_begin, type_end = offset_for_node(type, tree.tokens)
        type.kb_resources = run_task(Task.MAP_TYPE, {'text': question_text, 'type_begin': type_begin, 'type_end': type_end })

    # Map the relations
    # map_relations(tree)


answer("How many children does Barack Obama have?")
