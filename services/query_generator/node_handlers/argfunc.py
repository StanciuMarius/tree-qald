from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS
from services.query_generator.constants import BIND_PATTERN, ARGMAX_PATTERN, ARGMIN_PATTERN, ARGNTH_PATTERN

def handle_ARGMAX(gen, node: QueryTree.Node):
    handle_topn_helper(gen, node, 1)

def handle_TOPN(gen, node: QueryTree.Node):
    # literal = list(filter(lambda child: child.type = NodeType.LITERAL, node.children))[0]\
    literal = 4
    return handle_topn_helper(gen, node, literal)

def handle_ARGMIN(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    relation_uri = node.kb_resources[0]
    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        handle_subquery(gen, node, asc=True)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        handle_subquery(gen, node, asc=True)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(gen, node, e1, e2, relation_uri, '<')
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

def handle_2_entities(gen, node, e1, e2, relation, sign):
    relation_uri = node.kb_resources[0]
    v1, v2 = gen.generate_variable_name(), gen.generate_variable_name()
    gen.node_vs_reference[node.id] = gen.generate_variable_name()
    gen.triples.append((e1, relation_uri, v1))
    gen.triples.append((e2, relation_uri, v2))
    gen.filters.append(BIND_PATTERN.format(v1, sign, v2, e1, e2, gen.node_vs_reference[node.id]))

def handle_subquery(gen, node, asc=True, ordinal=None, limit=1):
    relation_uri = node.kb_resources[0]
    val = gen.generate_variable_name() 
    gen.triples.append((gen.node_vs_reference[node.id], relation_uri, val))
    if ordinal:
        gen.post_processing.append(ARGNTH_PATTERN.format(val, ordinal))
    elif asc:
        gen.post_processing.append(ARGMIN_PATTERN.format(val))
    else:
        gen.post_processing.append(ARGMAX_PATTERN.format(val, limit))


def handle_topn_helper(gen, node: QueryTree.Node, limit: int):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    relation_uri = node.kb_resources[0]
    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        handle_subquery(gen, node, asc=False, ordinal=None, limit=limit)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        handle_subquery(gen, node, asc=False, ordinal=None, limit=limit)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(gen, node, e1, e2, relation_uri, '>')
    else:
        # TODO handle union of arbitrary length entity sets
        print("Unsupported ARGMAX!")
        raise
    gen.add_type_restrictions(node)