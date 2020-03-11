import json
import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS, TRIPLE_PATTERN, RELATION_EXTRACTION_VARIABLE

def handle_EXISTS(gen, node: QueryTree.Node):
    gen.is_exists = True
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))

    if len(entity_sets) == 1:
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    else:
        # TODO handle union of multiple entity sets
        print("Unsupported EXISTS!")
        raise

def handle_EXISTSRELATION(gen, node: QueryTree.Node, reverse_relation=False):
    gen.is_exists = True
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literals = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))
    gen.node_vs_reference[node.id] = None
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE
    if len(entity_sets) == 2:
        e1, e2 = entity_sets
        triple = (gen.node_vs_reference[e1.id], relation, gen.node_vs_reference[e2.id])
        gen.triples.append(reversed(triple) if reverse_relation else triple)


    elif len(entity_sets) == 1 and len(literals) == 1:
        literal = literals[0].kb_resources[0]
        triple = (gen.node_vs_reference[entity_sets[0].id], relation, literal)
        gen.triples.append(reversed(triple) if reverse_relation else triple)



def handle_ISA(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    gen.add_type_restrictions(node)
    gen.is_exists = True