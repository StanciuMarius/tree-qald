import json
import os
import sys
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType
from services.query_generator.constants import QUERY_TEMPLATE_FILE_PATH, TYPE_RELATION, ENTITY_SETS

class QueryGenerator:

    def generate(self, query_tree: QueryTree):
        self.__handle_node(query_tree.root)
        root_variable = self.__node_vs_reference[query_tree.root]
        prefixes = ''
        filters = ''
        triples = ''
        for triple in self.__triples:
            triples += '\t{} {} {}.\n'.format(*triple)
        
        with open(QUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()

        post_process = ''
        
        final_query = template.format(ROOT_VARIABLE=root_variable, PREFIXES=prefixes, TRIPLES=triples, FILTERS=filters, POST_PROCESS=post_process)

        return final_query

    def __handle_node(self, node: QueryTree.Node):
        if node.type.value in self.__node_handlers:
            # Handle children first, then current node
            for child in node.children:
                self.__handle_node(child)
            self.__node_handlers[node.type.value](node)
    
    def __handle_ROOT(self, node: QueryTree.Node):
        entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
        if len(entity_sets) == 1:
            self.__node_vs_reference[node] = self.__node_vs_reference[entity_sets[0]]
        else:
            self.__node_vs_reference[node] = self.__generate_variable_name(node)
            self.__add_type_restrictions(node)

    def __handle_ARGMAX(self, node: QueryTree.Node):
        self
    def __handle_ARGMIN(self, node: QueryTree.Node): print(node.type.value)
    def __handle_ARGNTH(self, node: QueryTree.Node): print(node.type.value)
    def __handle_ARGMAXCOUNT(self, node: QueryTree.Node): print(node.type.value)
    def __handle_ARGMINCOUNT(self, node: QueryTree.Node): print(node.type.value)
    def __handle_COUNT(self, node: QueryTree.Node): print(node.type.value)
    def __handle_EXISTS(self, node: QueryTree.Node): print(node.type.value)
    def __handle_EXISTSRELATION(self, node: QueryTree.Node): print(node.type.value)
    def __handle_SAMPLE(self, node: QueryTree.Node): print(node.type.value)
    def __handle_ISGREATER(self, node: QueryTree.Node): print(node.type.value)
    def __handle_ISLESS(self, node: QueryTree.Node): print(node.type.value)
    def __handle_GREATER(self, node: QueryTree.Node): print(node.type.value)
    def __handle_LESS(self, node: QueryTree.Node): print(node.type.value)
    def __handle_TOPN(self, node: QueryTree.Node): print(node.type.value)
    def __handle_GREATERCOUNT(self, node: QueryTree.Node): print(node.type.value)
    def __handle_LESSCOUNT(self, node: QueryTree.Node): print(node.type.value)
    
    def __handle_ENTITY(self, node: QueryTree.Node):
        self.__node_vs_reference[node] = "<yoyster entity>"
    
    def __handle_PROPERTY(self, node: QueryTree.Node):
        variable = self.__generate_variable_name(node)
        relation_uri = '<yoyster relation>'

        self.__add_type_restrictions(node)
        entity_sets = list(filter(lambda child: child.type.value in ENTITY_SETS, node.children))
        for node in entity_sets:
            reference = self.__node_vs_reference[node]
            self.__triples.append((variable, relation_uri, reference))


    def __add_type_restrictions(self, node: QueryTree.Node) -> None:
        variable = self.__node_vs_reference[node]
        type_nodes = list(filter(lambda child: child.type == NodeType.TYPE, node.children))
        for type_node in type_nodes:
            type_uri = '<yoyster type>'
            self.__triples.append((variable, TYPE_RELATION, type_uri))
    
    def __generate_variable_name(self, node: QueryTree.Node) -> str:
        if not self.__variables:
            self.__variables.append('?a')
        else:
            self.__variables.append('?' + str(chr(ord(self.__variables[-1][-1]) + 1)))
        self.__node_vs_reference[node] = self.__variables[-1]
        return self.__variables[-1]

    def __init__(self):
        self.__node_vs_reference = {}
        self.__variables = []
        self.__triples = []
        self.__node_handlers = {
            'ROOT': self.__handle_ROOT,
            'ARGMAX': self.__handle_ARGMAX,
            'ARGMIN': self.__handle_ARGMIN,
            'ARGNTH': self.__handle_ARGNTH,
            'ARGMAXCOUNT': self.__handle_ARGMAXCOUNT,
            'ARGMINCOUNT': self.__handle_ARGMINCOUNT,
            'COUNT': self.__handle_COUNT,
            'EXISTS': self.__handle_EXISTS,
            'EXISTSRELATION': self.__handle_EXISTSRELATION,
            'SAMPLE': self.__handle_SAMPLE,
            'ISGREATER': self.__handle_ISGREATER,
            'ISLESS': self.__handle_ISLESS,
            'GREATER': self.__handle_GREATER,
            'LESS': self.__handle_LESS,
            'TOPN': self.__handle_TOPN,
            'GREATERCOUNT': self.__handle_GREATERCOUNT,
            'LESSCOUNT': self.__handle_LESSCOUNT,
            'PROPERTY': self.__handle_PROPERTY,
            'ENTITY': self.__handle_ENTITY
        }
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
    query_tree = query_trees[46]
    query_tree.pretty_print()
    query = QUERY_GENERATOR.generate(query_tree)
    print(query)
