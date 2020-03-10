import json
import os
import sys
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS, COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH, TRIPLE_PATTERN



def handle_GREATERCOUNT(gen, node: QueryTree.Node):
    return handle_comparatorCOUNT(gen, node, '>')

def handle_LESSCOUNT(gen, node: QueryTree.Node):
    return handle_comparatorCOUNT(gen, node, '>')

def handle_ISLESS(gen, node: QueryTree.Node):
    return handle_IScomparator(gen, node, '<')

def handle_ISGREATER(gen, node: QueryTree.Node):
    return handle_IScomparator(gen, node, '>')

def handle_comparatorCOUNT(gen, node:QueryTree.Node, comparator):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literal = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))[0].kb_resources[0]
    relation_uri = node.kb_resources[0]

    if len(entity_sets) == 1:
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    elif len(entity_sets) == 0:
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported GREATERCOUNT!")
        raise

    gen.add_type_restrictions(node)

    # We move all current triples into the subquery
    triples = ''.join([TRIPLE_PATTERN.format(*triple) for triple in gen.triples])
    gen.triples = []

    val = gen.generate_variable_name()
    val_count = gen.generate_variable_name()
    with open(COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
        template = query_template_file.read()
    gen.filters.append(template.format(ent=gen.node_vs_reference[node.id], val=val, val_count=val_count, relation=relation_uri, triples=triples, comparator=comparator, literal=literal))
    


def handle_LESS(gen, node: QueryTree.Node):
    handle_comparator(gen, node, '<')

def handle_GREATER(gen, node: QueryTree.Node):
    handle_comparator(gen, node, '>')

def handle_IScomparator(gen, node: QueryTree.Node, comparator):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    e_1_offset, _ = gen.query_tree.offset_for_node(entity_sets[0])
    e_2_offset, _ = gen.query_tree.offset_for_node(entity_sets[1])
    relation = node.kb_resources[0]
    
    e_1_val = gen.generate_variable_name()
    e_2_val = gen.generate_variable_name()

    if e_1_offset < e_2_offset:
        e_1, e_2 = entity_sets[0].kb_resources[0], entity_sets[1].kb_resources[0]
    else:
        e_2, e_1 = entity_sets[0].kb_resources[0], entity_sets[1].kb_resources[0]
    
    gen.triples.append((e_1, relation, e_1_val))
    gen.triples.append((e_2, relation, e_2_val))
    gen.filters.append('FILTER({} {} {})'.format(e_1_val, comparator, e_2_val))
    gen.is_exists = True
    

def handle_comparator(gen, node: QueryTree.Node, comparator):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literal = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))[0].kb_resources[0]
    relation_uri = node.kb_resources[0]

    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGMAX!")
        raise
    val = gen.generate_variable_name()
    gen.triples.append((gen.node_vs_reference[node.id], relation_uri, val))
    gen.filters.append('FILTER({} {} {})'.format(val, comparator, literal))
    gen.add_type_restrictions(node)