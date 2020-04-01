import json
import os
import sys
import traceback
from copy import deepcopy, copy
from typing import Tuple, List
sys.path.insert(0, os.getcwd())
from datasets.relation_extraction.cross_kb_relations.resolver import EquivalentRelationResolver
from datasets.knowledge_base.dbpedia.parser.dbpedia_occupations import DBPediaOccupationsDataset
from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from common.knowledge_base import COMPARABLE_DATATYPES
from services.tasks import run_task, Task
import services.query_generator.constants as constants
from services.query_generator.node_handlers.argfunc import handle_ARGMAX, handle_ARGMIN, handle_ARGNTH, handle_TOPN
from services.query_generator.node_handlers.misc import handle_ROOT, handle_PROPERTY, handle_PROPERTYCONTAINS, handle_ENTITY, handle_SAMPLE
from services.query_generator.node_handlers.count import handle_ARGMAXCOUNT, handle_ARGMINCOUNT, handle_COUNT
from services.query_generator.node_handlers.exists import handle_EXISTS, handle_EXISTSRELATION, handle_ISA
from services.query_generator.node_handlers.comparators import handle_GREATER, handle_LESS, handle_ISGREATER, handle_ISLESS, handle_GREATERCOUNT, handle_LESSCOUNT
from services.mapping.relation_mapping.relation_classifier.preprocessing import generate_relation_extraction_sequence
INORDER_TRIPLE_PATTERN = '\t{SUBJECT} {RELATION} {OBJECT}.\n'
REVERSE_ORDER_TRIPLE_PATTERN = '\t{OBJECT} {RELATION} {SUBJECT}.\n'
COMBINED_ORDER_TRIPLE_PATTERN = ('\t{{ {SUBJECT} {RELATION} {OBJECT}. VALUES {RELATION} {{ {IN_ORDER_RELATIONS} }} }} UNION \n' +
                                 '\t{{ {OBJECT} {RELATION} {SUBJECT}. VALUES {RELATION} {{ {REVERSE_ORDER_RELATIONS} }} }} \n')

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
        for entity in self.tree.root.collect({NodeType.ENTITY}):
            self.__map_entity(entity)
        for type   in self.tree.root.collect({NodeType.TYPE}):  
            self.__map_type(type)

        # Aggregate triples and constraints recursively (save them in the internal state)
        try:
            self.__handle_node(self.tree.root)

        # Generate the actual string of the SPARQL query from the internal state
            return_variable = self.node_vs_reference[self.tree.root.id]
            query: str = self.generate_query_from_current_state(return_variable)
        except:
            traceback.print_exc(file=sys.stdout)
            return None, None, self.tree

        return_variable_name = return_variable.replace('?', '') if not self.is_exists else '' # No return variable for ASK queries
        return query, return_variable_name, self.tree

    def generate_query_from_current_state(self, return_variable: str, alias: str = None) -> str:
        # Preprocess value 
        for variable, values in self.bindings.items():
            for index, value in enumerate(values):
                if '/' in value and '<' not in value: # if it's an uri we wrap it with angle brackets
                    values[index] = '<' + value + '>'
        
        unprocessed_bindings = copy(self.bindings)

        triples_text = ''
        for triple in self.triples:
            subject_variable, relation_variable, object_variable = triple
            relation_values = unprocessed_bindings[relation_variable] if relation_variable in self.bindings else []
            in_order_relation_values = [relation for relation in relation_values if relation[0:2] != '<_']
            reverse_order_relation_values = [relation.replace('<_', '<') for relation in relation_values if relation[0:2] == '<_']
            
            if in_order_relation_values and reverse_order_relation_values:
                triples_text += COMBINED_ORDER_TRIPLE_PATTERN.format(
                    SUBJECT=subject_variable,
                    RELATION=relation_variable,
                    OBJECT=object_variable,
                    IN_ORDER_RELATIONS=' '.join(in_order_relation_values),
                    REVERSE_ORDER_RELATIONS=' '.join(reverse_order_relation_values))
                # We added value bindings for the relation in this subquery (see COMBINED_ORDER_TRIPLE_PATTERN) so we can ommit them later
                unprocessed_bindings.pop(relation_variable)
            elif reverse_order_relation_values:
                unprocessed_bindings[relation_variable] = reverse_order_relation_values # Remove the '_'s
                triples_text += REVERSE_ORDER_TRIPLE_PATTERN.format(SUBJECT=subject_variable, RELATION=relation_variable, OBJECT=object_variable)
            else:
                triples_text += INORDER_TRIPLE_PATTERN.format(SUBJECT=subject_variable, RELATION=relation_variable, OBJECT=object_variable)

        bindings_text = '\n'.join([constants.VALUE_BINDING_PATTERN.format(variable, ' '.join(values)) for variable, values in unprocessed_bindings.items()])
        filters_text = '\n'.join(self.filters)
        body_text = '\n'.join([triples_text, filters_text, bindings_text])
        prefixes_text = '' # Try to avoid using prefixes
        post_processing_text = '\n'.join(self.post_processing)

        if alias: 
            with open(constants.SUBQUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file: template = query_template_file.read()
            final_query = template.format(BODY=body_text, PREFIXES=prefixes_text, POST_PROCESS=post_processing_text, VARIABLE=return_variable, ALIAS=alias)
        elif self.is_exists:
            with open(constants.EXISTS_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file: template = query_template_file.read()
            final_query = template.format(BODY=body_text, PREFIXES=prefixes_text, POST_PROCESS=post_processing_text)
        else:
            with open(constants.QUERY_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as query_template_file: template = query_template_file.read()
            final_query = template.format(BODY=body_text, PREFIXES=prefixes_text, POST_PROCESS=post_processing_text, VARIABLE=return_variable)

        return final_query

    def __handle_node(self, node: QueryTree.Node):
        # Nodes are handled recusively in reverse order
        if node.type in NODE_HANDLERS:
            for child in node.children:
                self.__handle_node(child)

            if node.type in RELATION_NODE_TYPES:
                self.__map_relation(node)
                NODE_HANDLERS[node.type](gen=self, node=node, reverse_relation=False)
            else:
                NODE_HANDLERS[node.type](self, node)

    def __map_entity(self, node: QueryTree.Node) -> None:
        node.children = list(filter(lambda x: x.type == NodeType.TOKEN, node.children)) # TODO: handle type constraints for entities
        entity_begin, entity_end = self.tree.offset_for_node(node)
        node.kb_resources = run_task(Task.MAP_ENTITY, {'text': self.question_text, 'entity_begin': entity_begin, 'entity_end': entity_end })

    def __map_type(self, node: QueryTree.Node) -> None:
        type_begin, type_end = self.tree.offset_for_node(node)
        node.kb_resources = run_task(Task.MAP_TYPE, {'text': self.question_text, 'type_begin': type_begin, 'type_end': type_end })

    def __map_relation(self, node: QueryTree.Node) -> bool:
        parent_node = self.tree.find_parent(node)
        if node.type == NodeType.EXISTSRELATION or parent_node.type == NodeType.EXISTS:
            # In case of EXISTS we can't consider prior candidates because mapping implies picking the most probable from
            # them. In this case EXISTS would always yield true. Instead, the strategy is to get the most probable relation from all relation search space.
            prior_candidates = []
        else:
            # We use the accumulated constraints so far to generate a query that retrieves all possible relations for this node.
            # Make copies so we don't break the current state
            node_copy = deepcopy(node)
            gen = deepcopy(self)
            NODE_HANDLERS[node.type](gen=gen, node=node_copy, reverse_relation=False)
            in_order_query  = gen.generate_query_from_current_state(constants.RELATION_EXTRACTION_VARIABLE)
            in_order_candidates = run_task(Task.RUN_SPARQL_QUERY, {'query_body': in_order_query, 'return_variable': constants.RELATION_EXTRACTION_VARIABLE.replace('?', '')})
            in_order_candidates = list(filter(lambda x: x not in constants.RELATION_MAPPING_BLACKLIST, in_order_candidates))
            
            prior_candidates = in_order_candidates
            
            # We also don't know the order yet (in terms of subject-object) of the triple yet, so we need the relation candidates for the revese order as well.
            if node.type not in {NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.TOPN}: # Can't reverse these
                node_copy = deepcopy(node)
                gen = deepcopy(self)
                NODE_HANDLERS[node.type](gen=gen, node=node_copy, reverse_relation=True)
                reverse_order_query  = gen.generate_query_from_current_state(constants.RELATION_EXTRACTION_VARIABLE)
                reverse_order_candidates = run_task(Task.RUN_SPARQL_QUERY, {'query_body': reverse_order_query, 'return_variable': constants.RELATION_EXTRACTION_VARIABLE.replace('?', '')})
                reverse_order_candidates = list(filter(lambda x: x not in constants.RELATION_MAPPING_BLACKLIST, reverse_order_candidates))
                reverse_order_candidates = [self.resolver.reverse_relation(candidate) for candidate in reverse_order_candidates]
                prior_candidates.extend(reverse_order_candidates)

            # Remove any candidates that already mapped  in reverse to a child node so as to avoid cycles
            child_relation_nodes = node.collect(RELATION_NODE_TYPES)
            child_relations = []
            for child in child_relation_nodes: child_relations.extend(child.kb_resources)
            reversed_child_relations = set([self.resolver.reverse_relation(relation) for relation in child_relations])
            prior_candidates = list(filter(lambda relation: relation not in reversed_child_relations, prior_candidates))


        relation_mapping_input = generate_relation_extraction_sequence(self.tree, node)
        relation_mapping_input['candidates'] = prior_candidates
        relations = run_task(Task.MAP_RELATIONS, relation_mapping_input)

        if node.type == NodeType.EXISTSRELATION or parent_node.type == NodeType.EXISTS:
            # In case of existence checking, consider both directions
            relations.extend([self.resolver.reverse_relation(relation) for relation in relations])

        node.kb_resources = relations

    def add_type_restrictions(self, node: QueryTree.Node) -> None:
        '''
            Expands type children nodes of the given node and adds "?node_var a <type>" triples
        '''
        type_nodes = list(filter(lambda child: child.type == NodeType.TYPE, node.children))
        variable = self.node_vs_reference[node.id]
        
        def handle_complex_types(node):
            # Person occupations (e.g. jobs, titles) are not necessarily linked via rdf:type, so they are treated differently
            type_texts = set([self.tree.text_for_node(node) for node in type_nodes])
            occupations = list(type_texts.intersection(self.occupations.occupations))
            
            if not occupations: return False

            type_uris = ' '.join([' '.join('<' + kb_resource + '>' for kb_resource in node.kb_resources) for node in type_nodes])
        
            occupation_filter = constants.OCCUPATION_FILTER_TEMPLATE.format(
                VARIABLE=variable,
                TYPES=type_uris,
                OCCUPATION=occupations[0]) # TODO consider all of them. Works with regex but it's too slow.
            
            self.filters.append(occupation_filter)
            return True
        
        if handle_complex_types(node): return

        for type_node in type_nodes:            
            if not type_node.kb_resources: continue # This shouldn't happen
            if type_node.kb_resources[0] in COMPARABLE_DATATYPES:
                self.add_datatype_restrictions(variable, type_node.kb_resources)
            else:
                type_variable = self.generate_variable_name()
                self.bindings[type_variable] = type_node.kb_resources
                self.triples.append((variable, constants.TYPE_RELATION, type_variable))
        
    def add_datatype_restrictions(self, variable: str, datatypes: List[str]):
        '''
            Datatype constraints are types for literals. Added via FILTER(datatype(?var) == <datatype> || etc..) statement
        '''
        constraints = constants.DATATYPE_FILTER_SEPARATOR.join([constants.DATATYPE_FILTER_ELEMENT.format(VARIABLE=variable, TYPE=datatype) for datatype in datatypes])
        statement = constants.DATATYPE_FILTER_WRAPPER.format(CONSTRAINTS=constraints)
        self.filters.append(statement)
    
    def generate_variable_name(self) -> str:
        if not self.__variables:
            self.__variables.append('?a')
        else:
            self.__variables.append('?' + str(chr(ord(self.__variables[-1][-1]) + 1)))
        return self.__variables[-1]

    def clear(self):
        self.triples = []
        self.filters = []
        self.post_processing = []
        self.bindings = {}

    def __init__(self):
        self.node_vs_reference = {}
        self.__variables = []
        self.triples = []
        self.filters = []
        self.is_exists = False
        self.post_processing = []
        self.tree = None
        self.bindings = {}
        self.resolver = EquivalentRelationResolver()
        self.occupations = DBPediaOccupationsDataset()

def generate_query(query_tree_dict: dict):
    generator = QueryGenerator()
    return generator(QueryTree.from_dict(query_tree_dict))


# INPUT_FILE_PATH = 'datasets\parsing\data\constituency_annotated_questions.json'
# with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as input_file:
#     questions = json.load(input_file)
#     tree = questions[59]
#     QueryTree.from_dict(tree).pretty_print()

#     query = generate_query(tree)


