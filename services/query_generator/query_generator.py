import json
import os
import sys
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import QUERY_TEMPLATE_FILE_PATH, TYPE_RELATION, ENTITY_SETS
from services.query_generator.node_handlers.argfunc import handle_ARGMAX, handle_ARGMIN, handle_ARGNTH
from services.query_generator.node_handlers.misc import handle_ROOT, handle_PROPERTY, handle_ENTITY
from services.query_generator.node_handlers.count import handle_ARGMAXCOUNT, handle_ARGMINCOUNT, handle_COUNT

TRIPLE_PATTERN = '\t{} {} {}.\n'
NODE_HANDLERS = {
    'ROOT': handle_ROOT,
    'ARGMAX': handle_ARGMAX,
    'ARGMIN': handle_ARGMIN,
    'ARGNTH': handle_ARGNTH,
    'PROPERTY': handle_PROPERTY,
    'ENTITY': handle_ENTITY,
    'ARGMAXCOUNT': handle_ARGMAXCOUNT,
    'ARGMINCOUNT': handle_ARGMINCOUNT,
    # 'COUNT': handle_COUNT,
    # 'EXISTS': handle_EXISTS,
    # 'EXISTSRELATION': handle_EXISTSRELATION,
    # 'SAMPLE': handle_SAMPLE,
    # 'ISGREATER': handle_ISGREATER,
    # 'ISLESS': handle_ISLESS,
    # 'GREATER': handle_GREATER,
    # 'LESS': handle_LESS,
    # 'TOPN': handle_TOPN,
    # 'GREATERCOUNT': handle_GREATERCOUNT,
    # 'LESSCOUNT': handle_LESSCOUNT,
}
class QueryGenerator:

    def generate(self, query_tree: QueryTree):
        self.__handle_node(query_tree.root)
        root_variable = self.node_vs_reference[query_tree.root]
        prefixes = ''
        triples = ''.join([TRIPLE_PATTERN.format(*triple) for triple in self.triples])
        filters = '\n'.join(self.filters)

        with open(QUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()

        post_processing = '\n'.join(self.post_processing)
        
        final_query = template.format(ROOT_VARIABLE=root_variable, PREFIXES=prefixes, TRIPLES=triples, FILTERS=filters, POST_PROCESS=post_processing)

        return final_query

    def __handle_node(self, node: QueryTree.Node):
        if node.type.value in NODE_HANDLERS:
            # Handle children first, then current node
            for child in node.children:
                self.__handle_node(child)
            NODE_HANDLERS[node.type.value](self, node)



    def add_type_restrictions(self, node: QueryTree.Node) -> None:
        variable = self.node_vs_reference[node]
        type_nodes = list(filter(lambda child: child.type == NodeType.TYPE, node.children))
        for type_node in type_nodes:
            type_uri = '<yoyster type>'
            self.triples.append((variable, TYPE_RELATION, type_uri))
    
    def generate_variable_name(self) -> str:
        if not self.__variables:
            self.__variables.append('?a')
        else:
            self.__variables.append('?' + str(chr(ord(self.__variables[-1][-1]) + 1)))
        return self.__variables[-1]

    def __init__(self):
        self.node_vs_reference = {}
        self.__variables = []
        self.triples = []
        self.filters = []
        self.post_processing = []

QUERY_GENERATOR = QueryGenerator()

def generate_query(query_tree_dict: dict):
    try:
        return QUERY_GENERATOR.generate_query(QueryTree.from_dict(query_tree_dict))
    except:
        return ''

INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'
with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
    questions = json.load(input_file)
    query_trees = list(map(lambda question: QueryTree.from_dict(question), questions))
    query_tree = query_trees[838]
    query_tree.pretty_print()
    query = QUERY_GENERATOR.generate(query_tree)
    print(query)
