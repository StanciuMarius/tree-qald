import json
import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS, TRIPLE_PATTERN

def handle_EXISTS(gen, node: QueryTree.Node):
    gen.is_exists = True
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))

    if len(entity_sets) == 1:
        gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
    else:
        # TODO handle union of multiple entity sets
        print("Unsupported EXISTS!")
        raise

def handle_EXISTSRELATION(gen, node: QueryTree.Node):
    gen.is_exists = True
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    literals = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))
    gen.node_vs_reference[node] = None
    relation = '<yoyster relation>'

    if len(entity_sets) == 2:
        e1, e2 = entity_sets
        gen.triples.append((gen.node_vs_reference[e1], relation, gen.node_vs_reference[e2]))
    elif len(entity_sets) == 1 and len(literals) == 1:
        literal = '<yoyster literal>'
        gen.triples.append((gen.node_vs_reference[entity_sets[0]], relation, literal))


def handle_ISA(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
    gen.add_type_restrictions(node)
    gen.is_exists = True