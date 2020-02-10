from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS

def handle_ROOT(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    if len(entity_sets) == 1:
        gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
    else:
        gen.node_vs_reference[node] = gen.generate_variable_name()
        gen.add_type_restrictions(node)

    
def handle_PROPERTY(gen, node: QueryTree.Node):
    gen.node_vs_reference[node] = gen.generate_variable_name()
    relation_uri = '<yoyster relation>'

    gen.add_type_restrictions(node)
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    for other_node in entity_sets:
        reference = gen.node_vs_reference[other_node]
        gen.triples.append((gen.node_vs_reference[node], relation_uri, reference))


def handle_ENTITY(gen, node: QueryTree.Node):
    gen.node_vs_reference[node] = "<yoyster entity>"
