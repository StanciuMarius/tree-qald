from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS
from services.query_generator.constants import BIND_PATTERN

def handle_ARGMAX(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    relation_uri = '<yoyster relation>'
    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
        handle_subquery(gen, node, entity_sets[0], asc=False)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node] = gen.generate_variable_name()
        handle_subquery(gen, node, entity_sets[0], asc=False)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(generator, node, e1, e2, relation_uri, '>')
    else:
        print("Unsupported ARGMIN!")
        raise
    gen.add_type_restrictions(node)

def handle_ARGMIN(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    relation_uri = '<yoyster relation>'
    if len(entity_sets) == 1: # Subquery
        gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
        handle_subquery(gen, node, entity_sets[0], asc=True)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node] = gen.generate_variable_name()
        handle_subquery(gen, node, entity_sets[0], asc=True)
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        e1, e2 = entity_sets
        handle_2_entities(generator, node, e1, e2, relation_uri, '<')
    else:
        print("Unsupported ARGMIN!")
        raise
    gen.add_type_restrictions(node)

def handle_ARGNTH(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    # literal = list(filter(lambda child: child.type = NodeType.LITERAL, node.children))[0]\
    literal = '<yoyster literal>'
    if len(entity_sets) == 1:
        handle_subquery(gen, node, entity_sets[0], asc=True, ordinal=literal)
    elif len(entity_sets) == 0: # Type only
        gen.node_vs_reference[node] = gen.generate_variable_name()
        handle_subquery(gen, node, entity_sets[0], asc=True, ordinal=literal)
    else:
        print("Unsupported ARGNTH!")
        raise
    gen.add_type_restrictions(node)

def handle_2_entities(gen, node, e1, e2, relation, sign):
    relation_uri = '<yoyster relation>'
    v1, v2 = gen.generate_variable_name(), gen.generate_variable_name()
    gen.node_vs_reference[node] = gen.generate_variable_name()
    gen.triples.append((e1, relation_uri, e1_val))
    gen.triples.append((e2, relation_uri, e2_val))
    gen.filters.append(BIND_PATTERN.format(v1, sign, v2, e1, e2, gen.node_vs_reference[node]))

def handle_subquery(gen, node, subquery_node, asc=True, ordinal=None):
    relation_uri = '<yoyster relation>'
    val = gen.generate_variable_name() 
    gen.triples.append((gen.node_vs_reference[node], relation_uri, val))
    if ordinal:
        gen.post_processing.append(ARGNTH_PATTERN.format(val, ordinal))
    elif asc:
        gen.post_processing.append(ARGMIN_PATTERN.format(val))
    else:
        gen.post_processing.append(ARGMAX_PATTERN.format(val))
