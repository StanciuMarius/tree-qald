from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS
import services.query_generator.constants as constants

def handle_COUNT(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    alias = gen.generate_variable_name()

    if len(entity_sets) == 0: # Count type enumeration
        var = gen.generate_variable_name()
        gen.node_vs_reference[node.id] = var
        gen.add_type_restrictions(node)
        return_var = constants.COUNT_VARIABLE_PATTERN.format(var)
    else:
        return_var = '+'.join([constants.COUNT_VARIABLE_PATTERN.format(gen.node_vs_reference[entity_set.id]) for entity_set in entity_sets]) # Not tested for multiple entity_sets

    gen.node_vs_reference[node.id] = alias
    subquery = gen.generate_query_from_current_state(return_var, alias)
    gen.clear() # Everything was handleded in the subquery
    gen.filters.append(subquery)

def handle_ARGMAXCOUNT(gen, node: QueryTree.Node):
    return handle_ARGfuncCOUNT(gen, node, 'MAX')

def handle_ARGMINCOUNT(gen, node: QueryTree.Node):
    return handle_ARGfuncCOUNT(gen, node, 'MIN')

def handle_ARGfuncCOUNT(gen, node: QueryTree.Node, func = 'MAX'):
    entity_sets = list(filter(lambda child: child.type in ENTITY_SETS, node.children))
    if node.kb_resources:
        relation = gen.generate_variable_name()
        gen.bindings[relation] = node.kb_resources
    else:
        relation = constants.RELATION_EXTRACTION_VARIABLE

    if len(entity_sets) == 1 or len(entity_sets) == 0: # Subquery
        if len(entity_sets) == 1:
            gen.node_vs_reference[node.id] = gen.node_vs_reference[entity_sets[0].id]
        else:
            gen.node_vs_reference[node.id] = gen.generate_variable_name()
        
        gen.add_type_restrictions(node)

        # We move all current triples into the subquery
        triples = ''.join([constants.TRIPLE_PATTERN.format(*triple) for triple in gen.triples])
        gen.triples = []

        val = gen.generate_variable_name()
        val_count = gen.generate_variable_name()
        with open(constants.ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()
        order = 'DESC' if func == 'MAX' else 'ASC'

        gen.filters.append(template.format(ent=gen.node_vs_reference[node.id], val=val, val_count=val_count, relation=relation, triples=triples, order=order))
   
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        gen.node_vs_reference[node.id] = gen.generate_variable_name()
        e1 = gen.generate_variable_name()
        gen.bindings[e1] = entity_sets[0].kb_resources

        e2 = gen.generate_variable_name()
        gen.bindings[e2] = entity_sets[1].kb_resources

        val_1 = gen.generate_variable_name()
        val_2 = gen.generate_variable_name()
        val_count_1 = gen.generate_variable_name()
        val_count_2 = gen.generate_variable_name()

        with open(constants.COUNT_ENTITY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()
        sign = '>' if func == 'MAX' else '<'
        gen.filters.append(constants.BIND_PATTERN.format(val_count_1, sign, val_count_2, e1, e2, gen.node_vs_reference[node.id]))
        gen.filters.append(template.format(var=e1, relation=relation, val=val_1, val_count=val_count_1, triples=''))
        gen.filters.append(template.format(var=e2, relation=relation, val=val_2, val_count=val_count_2, triples=''))
    else:
        # TODO handle union of multiple entity sets
        print("Unsupported ARGfuncCOUNT!")
        raise