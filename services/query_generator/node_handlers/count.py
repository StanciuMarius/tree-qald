from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import ENTITY_SETS
from services.query_generator.constants import COUNT_SUBQUERY_TEMPLATE_FILE_PATH, ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH, COUNT_ENTITY_TEMPLATE_FILE_PATH, TRIPLE_PATTERN, BIND_PATTERN


def handle_COUNT(gen, node: QueryTree.Node):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))

    if len(entity_sets) == 0: # Count type enumeration
        var = gen.generate_variable_name()
        gen.node_vs_reference[node] = var
        gen.add_type_restrictions(node)
    else:
        var = '+'.join([gen.node_vs_reference[entity_set] for entity_set in entity_sets]) # Not tested for multiple entity_sets

    triples = ''.join([TRIPLE_PATTERN.format(*triple) for triple in gen.triples])
    filters = ''.join(gen.filters)
    post_processing = ''.join(gen.post_processing)
    
    gen.triples = []
    gen.filters = []
    gen.post_processing = [] 
    with open(COUNT_SUBQUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
        template = query_template_file.read()

    var_count = gen.generate_variable_name()
    gen.filters.append(template.format(TRIPLES=triples, FILTERS=filters, POST_PROCESS=post_processing, VAR_COUNT=var_count, VAR=var))
    gen.node_vs_reference[node] = var_count

def handle_ARGMAXCOUNT(gen, node: QueryTree.Node):
    return handle_ARGfuncCOUNT(gen, node, 'MAX')

def handle_ARGMINCOUNT(gen, node: QueryTree.Node):
    return handle_ARGfuncCOUNT(gen, node, 'MIN')

def handle_ARGfuncCOUNT(gen, node: QueryTree.Node, func = 'MAX'):
    entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
    relation_uri = '<yoyster relation>'

    if len(entity_sets) == 1 or len(entity_sets) == 0: # Subquery
        if len(entity_sets) == 1:
            gen.node_vs_reference[node] = gen.node_vs_reference[entity_sets[0]]
        else:
            gen.node_vs_reference[node] = gen.generate_variable_name()
        
        gen.add_type_restrictions(node)

        # We move all current triples into the subquery
        triples = ''.join([TRIPLE_PATTERN.format(*triple) for triple in gen.triples])
        gen.triples = []

        val = gen.generate_variable_name()
        val_count = gen.generate_variable_name()
        with open(ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()
        order = 'DESC' if func == 'MAX' else 'ASC'
        gen.filters.append(template.format(ent=gen.node_vs_reference[node], val=val, val_count=val_count, relation=relation_uri, triples=triples, order=order))
   
    elif len(entity_sets) == 2 and entity_sets[0].type == NodeType.ENTITY and entity_sets[1].type == NodeType.ENTITY:
        gen.node_vs_reference[node] = gen.generate_variable_name()
        relation_uri = '<yoyster relation>'
        ent_1 = '<yoyster entity1>'
        ent_2 = '<yoyster entity2>'
        val_1 = gen.generate_variable_name()
        val_2 = gen.generate_variable_name()
        val_count_1 = gen.generate_variable_name()
        val_count_2 = gen.generate_variable_name()

        with open(COUNT_ENTITY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()
        sign = '>' if func == 'MAX' else '<'
        gen.filters.append(BIND_PATTERN.format(val_count_1, sign, val_count_2, ent_1, ent_2, gen.node_vs_reference[node]))
        gen.filters.append(template.format(var=ent_1, relation=relation_uri, val=val_1, val_count=val_count_1, triples=''))
        gen.filters.append(template.format(var=ent_2, relation=relation_uri, val=val_2, val_count=val_count_2, triples=''))
    else:
        # TODO handle union of multiple entity sets
        print("Unsupported ARGfuncCOUNT!")
        raise