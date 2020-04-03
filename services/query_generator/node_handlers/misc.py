from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS, RELATION_EXTRACTION_VARIABLE

def handle_ROOT(gen, node: QueryTree.Node):
    non_types = list(filter(lambda child: child.type != NodeType.TYPE, node.children))
    if len(non_types) == 1 and not gen.is_exists:
        gen.node_vs_reference[node.id] = gen.node_vs_reference[non_types[0].id]
    else:
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        gen.add_type_restrictions(node)

    
def handle_PROPERTY(gen, node: QueryTree.Node, reverse_relation=False):
    gen.node_vs_reference[node.id] = gen.generate_variable_name()
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE
    gen.add_type_restrictions(node)
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    literals = list(filter(lambda child: child.type in {NodeType.LITERAL}, node.children))

    for other_node in entity_sets:
        reference = gen.node_vs_reference[other_node.id]
        triple = (gen.node_vs_reference[node.id], relation, reference)
        gen.triples.append(reversed(triple) if reverse_relation else triple)

    if literals:
        literal_variable = gen.generate_variable_name()
        literal_text = gen.tree.text_for_node(literals[0])
        triple = (gen.node_vs_reference[node.id], relation, literal_variable)
        gen.bindings[literal_variable] = ["\"{}\"".format(literal_text)]
        gen.triples.append(reversed(triple) if reverse_relation else triple)


def handle_PROPERTYCONTAINS(gen, node: QueryTree.Node, reverse_relation=False):
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = RELATION_EXTRACTION_VARIABLE

    entity_set = list(filter(lambda child: child.type in ENTITY_SETS and child.type != NodeType.ENTITY, node.children))
    entity = list(filter(lambda child: child.type == NodeType.ENTITY, node.children))

    gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_set[0].id]
    gen.add_type_restrictions(node)

    triple = (gen.node_vs_reference[entity_set[0].id], relation, gen.node_vs_reference[entity[0].id])
    gen.triples.append(reversed(triple) if reverse_relation else triple)

    
def handle_ENTITY(gen, node: QueryTree.Node):
    gen.node_vs_reference[node.id] = gen.generate_variable_name()
    gen.bindings[gen.node_vs_reference[node.id]] = node.kb_resources


def handle_SAMPLE(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))

    if len(entity_sets) == 1:
        gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
    else:
        gen.node_vs_reference[node.id] = gen.generate_variable_name()

    gen.add_type_restrictions(node)
    index = 0 # TODO change to random
    gen.post_processing.append('OFFSET {} LIMIT 1\n'.format(index))
