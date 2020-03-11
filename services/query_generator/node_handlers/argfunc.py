from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS
from services.query_generator.constants import BIND_PATTERN, ARGMAX_PATTERN, ARGMIN_PATTERN, ARGNTH_PATTERN, RELATION_EXTRACTION_VARIABLE

def handle_ARGMAX(gen, node: QueryTree.Node):
    handle_topn_helper(gen, node, 1)

def handle_TOPN(gen, node: QueryTree.Node):
    # literal = list(filter(lambda child: child.type = NodeType.LITERAL, node.children))[0]\
    literal = 4
    return handle_topn_helper(gen, node, literal)

def handle_ARGMIN(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        handle_subquery(gen, node, asc=True)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        handle_subquery(gen, node, asc=True)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(gen, node, e1, e2, relation, '<')
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGMIN!")
        raise
    gen.add_type_restrictions(node)

def handle_ARGNTH(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literal = list(filter(lambda child: child.type == NodeType.LITERAL, node.children))[0].kb_resources[0]

    if len(entity_sets) == 1:
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        handle_subquery(gen, node, asc=True, ordinal=literal)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        handle_subquery(gen, node, asc=True, ordinal=literal)
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGNTH!")
        raise
    gen.add_type_restrictions(node)

def handle_2_entities(gen, node, e1, e2, relation, sign, reverse_relation=False):
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    v1, v2 = gen.generate_variable_name(), gen.generate_variable_name()
    gen.node_vs_reference[node.id] = gen.generate_variable_name()
    if reverse_relation:
        gen.triples.append((v1, relation, e1))
        gen.triples.append((v2, relation, e2))
    else:
        gen.triples.append((e1, relation, v1))
        gen.triples.append((e2, relation, v2))
    gen.filters.append(BIND_PATTERN.format(v1, sign, v2, e1, e2, gen.node_vs_reference[node.id]))

def handle_subquery(gen, node, asc=True, ordinal=None, limit=1, reverse_relation=False):
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    val = gen.generate_variable_name()
    
    triple = (gen.node_vs_reference[node.id], relation, val)
    gen.triples.append(reversed(triple) if reverse_relation else triple)

    
    if ordinal:
        gen.post_processing.append(ARGNTH_PATTERN.format(val, ordinal))
    elif asc:
        gen.post_processing.append(ARGMIN_PATTERN.format(val))
    else:
        gen.post_processing.append(ARGMAX_PATTERN.format(val, limit))


def handle_topn_helper(gen, node: QueryTree.Node, limit: int, reverse_relation=False):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        handle_subquery(gen, node, asc=False, ordinal=None, limit=limit, reverse_relation=reverse_relation)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        handle_subquery(gen, node, asc=False, ordinal=None, limit=limit, reverse_relation=reverse_relation)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(gen, node, e1, e2, relation, '>', reverse_relation)
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGMAX!")
        raise
    gen.add_type_restrictions(node)