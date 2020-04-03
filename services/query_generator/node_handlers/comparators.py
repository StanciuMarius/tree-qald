import json
import os
import sys
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import RELATION_EXTRACTION_VARIABLE, ENTITY_SETS, COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH, TRIPLE_PATTERN, RELATION_EXTRACTION_VARIABLE
from services.query_generator.literals import parse_number


def handle_GREATERCOUNT(gen, node: QueryTree.Node, reverse_relation=False):
    return handle_comparatorCOUNT(gen, node, '>', reverse_relation)

def handle_LESSCOUNT(gen, node: QueryTree.Node, reverse_relation=False):
    return handle_comparatorCOUNT(gen, node, '>', reverse_relation)

def handle_ISLESS(gen, node: QueryTree.Node, reverse_relation=False):
    return handle_IScomparator(gen, node, '<', reverse_relation)

def handle_ISGREATER(gen, node: QueryTree.Node, reverse_relation=False):
    return handle_IScomparator(gen, node, '>', reverse_relation)

def handle_comparatorCOUNT(gen, node:QueryTree.Node, comparator, reverse_relation=False):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    
    literal = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))[0]
    literal = parse_number(gen.tree.text_for_node(literal))

    relation = gen.generate_variable_name()
    gen.bindings[relation] = node.kb_resources
    
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
    # TODO: relation_uri...?
    gen.filters.append(template.format(ent=gen.node_vs_reference[node.id], val=val, val_count=val_count, relation=relation, triples=triples, comparator=comparator, literal=literal))
    


def handle_LESS(gen, node: QueryTree.Node, reverse_relation=False):
    handle_comparator(gen, node, '<', reverse_relation)

def handle_GREATER(gen, node: QueryTree.Node, reverse_relation=False):
    handle_comparator(gen, node, '>', reverse_relation)

def handle_IScomparator(gen, node: QueryTree.Node, comparator, reverse_relation=False):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    e1_offset, _ = gen.tree.offset_for_node(entity_sets[0])
    e2_offset, _ = gen.tree.offset_for_node(entity_sets[1])
    
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE
    
    e1 = gen.generate_variable_name()
    e2 = gen.generate_variable_name()
    e1_value = gen.generate_variable_name()
    e2_value = gen.generate_variable_name()

    if e1_offset < e2_offset:
        gen.bindings[e1_variable] = entity_sets[0].kb_resources
        gen.bindings[e2_variable] = entity_sets[1].kb_resources
    else:
        gen.bindings[e1_variable] = entity_sets[1].kb_resources
        gen.bindings[e2_variable] = entity_sets[0].kb_resources
    
    if reverse_relation:
        gen.triples.append((e1_value, relation, e1))
        gen.triples.append((e2_value, relation, e2))
    else:
        gen.triples.append((e1, relation, e1_value))
        gen.triples.append((e2, relation, e2_value))

    gen.filters.append('FILTER({} {} {})'.format(e1_value, comparator, e2_value))
    gen.is_exists = True
    

def handle_comparator(gen, node: QueryTree.Node, comparator, reverse_relation=False):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literal = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))[0].kb_resources[0]
    literal = parse_number(gen.tree.text_for_node(literal))

    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGMAX!")
        raise
    val = gen.generate_variable_name()

    triple = (gen.node_vs_reference[node.id], relation, val)
    gen.triples.append(reversed(triple) if reverse_relation else triple)

    gen.filters.append('FILTER({} {} {})'.format(val, comparator, literal))
    gen.add_type_restrictions(node)