


from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
QUESTION_WORDS = {'who', 'when', 'what', 'how', 'which'}

def offset_for_node_union(tree: QueryTree, nodes):
    union_begin, union_end = tree.offset_for_node(nodes[0])
    for node in nodes[1:]:
        node_begin, node_end = tree.offset_for_node(node)
        union_begin = min(union_begin, node_begin)
        union_end = max(union_end, node_end)
    return union_begin, union_end

def generate_relation_extraction_sequences(tree: QueryTree):
    text = ' '.join(tree.tokens)
    relation_nodes = tree.root.collect(RELATION_NODE_TYPES)

    node_vs_sequence = {}

    for node in relation_nodes:
        # Generate one sequence for each relation node
        sequence = text

        e1_nodes = []
        e2_nodes = []

        if node.type in {NodeType.EXISTSRELATION}:
            # Relation is between 2 entities/literal
            e1_nodes = [node.children[0]]
            e2_nodes = [node.children[1]]
        elif node.type in {NodeType.GREATER, NodeType.LESS}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.LITERAL, node.children))
            e2_nodes = list(filter(lambda x: x.type in {NodeType.LITERAL}, node.children))
        elif node.type in {NodeType.PROPERTY}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE, node.children))
            # We can consider a type as a substitute for entities
            # e.g. Give me all [E1] songs [/E1] by [E2] Bruce Springsteen [/E2].
            e2_nodes = list(filter(lambda x: x.type in {NodeType.TYPE}, node.children))[:1] # TODO: currently only consider first type
        elif node.type in {NodeType.PROPERTYCONTAINS}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.ENTITY and x.type != NodeType.LITERAL, node.children))
            e2_nodes = list(filter(lambda x: x.type == NodeType.ENTITY or x.type == NodeType.LITERAL, node.children))
        elif node.type in {NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.ARGMAXCOUNT, NodeType.ARGMINCOUNT, NodeType.TOPN, NodeType.GREATERCOUNT}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.LITERAL, node.children))


        e1_begin, e1_end = offset_for_node_union(tree, e1_nodes)

        if len(e2_nodes) == 0:
            if node.type == NodeType.PROPERTY and tree.tokens[0].lower() in QUESTION_WORDS and node in tree.root.children:
                # We can consider the question word as one of the entities for the direct child of a root
                # e.g. [E1] Who [/E1] is the wife of [E2] Barack Obama [/E2] ?
                e2_begin = 0
                e2_end = len(tree.tokens[0])
            else:
                # We only have one entity, so we add a dummy token at the beginning of the sequence to consider as E2
                new_token = ' [{}] '.format(node.type.value)
                sequence = new_token + sequence
                offset = len(new_token)
                e1_begin, e1_end, e2_begin, e2_end = offset + e1_begin, offset + e1_end, 0, offset
        else: 
            e2_begin, e2_end = offset_for_node_union(tree, e2_nodes)

        node_vs_sequence[node.id] = {
            'text': sequence,
            'id': '{}${}'.format(tree.id, node.id),
            'subject_begin': e1_begin,
            'subject_end': e1_end,
            'object_begin': e2_begin,
            'object_end': e2_end
        }
    return node_vs_sequence