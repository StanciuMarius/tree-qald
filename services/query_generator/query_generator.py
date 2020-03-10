import json
import os
import sys
from copy import deepcopy
from typing import Tuple
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from services.tasks import run_task, Task
from services.query_generator.constants import QUERY_TEMPLATE_FILE_PATH, EXISTS_TEMPLATE_FILE_PATH, TYPE_RELATION, ENTITY_SETS, RELATION_VARIABLE
from services.query_generator.node_handlers.argfunc import handle_ARGMAX, handle_ARGMIN, handle_ARGNTH, handle_TOPN
from services.query_generator.node_handlers.misc import handle_ROOT, handle_PROPERTY, handle_PROPERTYCONTAINS, handle_ENTITY, handle_SAMPLE
from services.query_generator.node_handlers.count import handle_ARGMAXCOUNT, handle_ARGMINCOUNT, handle_COUNT
from services.query_generator.node_handlers.exists import handle_EXISTS, handle_EXISTSRELATION, handle_ISA
from services.query_generator.node_handlers.comparators import handle_GREATER, handle_LESS, handle_ISGREATER, handle_ISLESS, handle_GREATERCOUNT, handle_LESSCOUNT
from services.mapping.relation_mapping.relation_classifier.preprocessing import generate_relation_extraction_sequence

TRIPLE_PATTERN = '\t{} {} {}.\n'
NODE_HANDLERS = {
    NodeType.ROOT: handle_ROOT,
    NodeType.ARGMAX: handle_ARGMAX,
    NodeType.ARGMIN: handle_ARGMIN,
    NodeType.ARGNTH: handle_ARGNTH,
    NodeType.PROPERTY: handle_PROPERTY,
    NodeType.PROPERTYCONTAINS: handle_PROPERTYCONTAINS,
    NodeType.ENTITY: handle_ENTITY,
    NodeType.ARGMAXCOUNT: handle_ARGMAXCOUNT,
    NodeType.ARGMINCOUNT: handle_ARGMINCOUNT,
    NodeType.COUNT: handle_COUNT,
    NodeType.EXISTS: handle_EXISTS,
    NodeType.EXISTSRELATION: handle_EXISTSRELATION,
    NodeType.SAMPLE: handle_SAMPLE,
    NodeType.GREATER: handle_GREATER,
    NodeType.LESS: handle_LESS,
    NodeType.TOPN: handle_TOPN,
    NodeType.ISGREATER: handle_ISGREATER,
    NodeType.ISLESS: handle_ISLESS,
    NodeType.GREATERCOUNT: handle_GREATERCOUNT,
    NodeType.LESSCOUNT: handle_LESSCOUNT,
    NodeType.ISA: handle_ISA,
}
class QueryGenerator(object):
    def __call__(self, tree: QueryTree):
        self.tree = tree
        self.question_text = ' '.join(self.tree.tokens)
        
        # We first map the entities and types since they don't require any contextual information apart from the question text
        # for entity in self.tree.root.collect({NodeType.ENTITY}):
        #     self.__map_entity(entity)
        # for type   in self.tree.root.collect({NodeType.TYPE}):  
        #     self.__map_type(type)

        # Aggregate triples and constraints recursively (save them in the internal state)
        self.__handle_node(self.tree.root)

        # Generate the actual string of the SPARQL query from the internal state
        return_variable = self.node_vs_reference[self.tree.root.id]
        query: str = self.__generate_query_from_current_state(return_variable)

        return query

    def __generate_query_from_current_state(self, return_variable: str) -> str:
        def preprocess_triple(triple: Tuple[str]):
            result = list(triple)
            for index, resource in enumerate(result):
                if '/' in resource: # if it's an uri we wrap it with angle brackets
                    result[index] = '<' + resource + '>'
            return result
        prefixes = ''
        triples  = ''.join([TRIPLE_PATTERN.format(*preprocess_triple(triple)) for triple in self.triples])
        filters  = '\n'.join(self.filters)

        template_file_path = EXISTS_TEMPLATE_FILE_PATH if self.is_exists else QUERY_TEMPLATE_FILE_PATH
        with open(template_file_path, 'r', encoding='utf-8') as query_template_file:
            template = query_template_file.read()

        post_processing = '\n'.join(self.post_processing)
        if self.is_exists:
            final_query = template.format(TRIPLES=triples, PREFIXES=prefixes, FILTERS=filters, POST_PROCESS=post_processing)
        else:
            final_query = template.format(ROOT_VARIABLE=return_variable, PREFIXES=prefixes, TRIPLES=triples, FILTERS=filters, POST_PROCESS=post_processing)

        return final_query

    def __handle_node(self, node: QueryTree.Node):
        # Nodes are handled recusively in reverse order
        if node.type in NODE_HANDLERS:
            for child in node.children:
                self.__handle_node(child)

            if node.type in RELATION_NODE_TYPES:
                self.__map_relation(node)
                
            NODE_HANDLERS[node.type](self, node)

    def __map_entity(self, node: QueryTree.Node) -> None:
        # entity_begin, entity_end = self.tree.offset_for_node(node)
        # node.kb_resources = run_task(Task.MAP_ENTITY, {'text': self.question_text, 'entity_begin': entity_begin, 'entity_end': entity_end })
        node.kb_resources = '<yoyster entity>'

    def __map_type(self, node: QueryTree.Node) -> None:
        # type_begin, type_end = self.tree.offset_for_node(node)
        # node.kb_resources = run_task(Task.MAP_TYPE, {'text': self.question_text, 'type_begin': type_begin, 'type_end': type_end })
        node.kb_resources = '<yoyster type>'

    def __map_relation(self, node: QueryTree.Node) -> None:
        # Make copies so we don't break the current state
        gen = deepcopy(self)
        node_copy = deepcopy(node)
        
        # We use the accumulated constraints so far to generate a query that retrieves all possible relations for this node.
        # We use a temporary placeholder variable for the relation of this node
        node_copy.kb_resources = [RELATION_VARIABLE] # TODO: relation and inverse in the same time
        NODE_HANDLERS[node.type](gen, node_copy)
        relation_query  = gen.__generate_query_from_current_state(RELATION_VARIABLE)
        relation_candidates = run_task(Task.RUN_SPARQL_QUERY, {'query_body': relation_query, 'return_variable': RELATION_VARIABLE.replace('?', '')})
        
        # Rank the obtained candidates
        relation_ranking_input = generate_relation_extraction_sequence(self.tree, node_copy)
        relation_ranking_input['candidates'] = relation_candidates
        relation_candidates = run_task(Task.RANK_RELATIONS, relation_ranking_input)

        # Pick the top candidate
        node.kb_resources = [relation_candidates[0]]
        

    def add_type_restrictions(self, node: QueryTree.Node) -> None:
        variable = self.node_vs_reference[node.id]
        type_nodes = list(filter(lambda child: child.type == NodeType.TYPE, node.children))
        for type_node in type_nodes:
            type_uri = type_node.kb_resources[0]
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
        self.is_exists = False
        self.post_processing = []
        self.tree = None
    

def generate_query(query_tree_dict: dict):
    generator = QueryGenerator()
    return generator(QueryTree.from_dict(query_tree_dict))


# INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'
# with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
#     questions = json.load(input_file)
#     tree = questions[58]
#     QueryTree.from_dict(tree).pretty_print()

#     query = generate_query(tree)


