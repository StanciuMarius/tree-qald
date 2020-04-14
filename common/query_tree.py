import os
import sys
sys.path.insert(0, os.getcwd())

from enum import Enum
from typing import List, Set
from pptree import print_tree

class NodeType(Enum):
    # The answer of a query
    ROOT = 'ROOT'
    
    # Computes the cardinal of a set of entities
    COUNT = 'COUNT'

    # Picks the entity from a set with the highest value for a particular relation (to be extracted)
    ARGMAX = 'ARGMAX'

    # Picks the entity from a set with the lowest value for a particular relation (to be extracted)
    ARGMIN = 'ARGMIN'

    # Picks the entity from a set with the highest cardinal for a particular relation
    ARGMAXCOUNT = 'ARGMAXCOUNT'

    # Picks the entity from a set with the lowest cardinal for a particular relation
    ARGMINCOUNT = 'ARGMINCOUNT'

    # Picks the entity from a set with the n-th lowest value (to be extracted)
    ARGNTH = 'ARGNTH'

    # Returns true if the given set is not empty
    EXISTS = 'EXISTS'

    # Pick a random sample from a set of entities
    SAMPLE = 'SAMPLE'
    
    # Returns true if a property exists between two given properties
    EXISTSRELATION = 'EXISTSRELATION'

    # Returns true if the first entity has a property value greater than the second's
    ISGREATER = 'ISGREATER'
    
    # Returns true if the first entity has a property value less than the second's
    ISLESS = 'ISLESS'

    # Returns true if the type of the given entity matches the given type
    ISA = 'ISA'

    # Filters the entities with a relation value (to be extracted) greater than a given value
    GREATER = 'GREATER'

    # Filters the entities with a relation value (to be extracted) less than a given value
    LESS = 'LESS'

    # Retrieves the top n entities sorted by a property value
    TOPN = 'TOPN'

    # Filters the entities with a cardinal of property (to be extracted) greater than a given literal
    GREATERCOUNT = 'GREATERCOUNT'
    
    # Filters the entities with a cardinal of property (to be extracted) less than a given literal
    LESSCOUNT = 'LESSCOUNT'

    # PROPERTY is the object of an RDF triple
    PROPERTY = 'PROPERTY'

    # Filters ENTITYSET by object containing the child entity or literal
    PROPERTYCONTAINS = 'PROPERTYCONTAINS'

    # Tokens that represent knowledge base TYPE+. E.g. "comonauts" "writer" 
    TYPE = 'TYPE'

    # Tokens that represent knowledge base entities. E.g. "Barack Obama", "Titanic"
    ENTITY = 'ENTITY'

    # Tokens that represent literals. E.g. "100", "15th of June", "1999", "1.0", "Frank the Tank"
    LITERAL = 'LITERAL'

    # Unused tokens
    UNUSED = 'UNUSED'

    # WH-words
    VARIABLE = 'VARIABLE'

    # A token
    TOKEN = 'TOKEN'

# Nodes that correspond to a Knowledge Base relation, hence they need mapping.
RELATION_NODE_TYPES = {
    NodeType.PROPERTY,
    NodeType.PROPERTYCONTAINS,
    NodeType.ARGMAXCOUNT,
    NodeType.ARGMINCOUNT,
    NodeType.ARGMAX,
    NodeType.ARGMIN,
    NodeType.ARGNTH,
    NodeType.EXISTSRELATION,
    NodeType.GREATER,
    NodeType.GREATERCOUNT,
    NodeType.LESS,
    NodeType.TOPN,
    NodeType.ISGREATER,
    NodeType.ISLESS,
}
ENTITY_SET_TYPES = {
    NodeType.PROPERTY,
    NodeType.PROPERTYCONTAINS,
    NodeType.SAMPLE,
    NodeType.ARGMAX,
    NodeType.ARGMIN,
    NodeType.ARGNTH,
    NodeType.ARGMAXCOUNT,
    NodeType.ARGMINCOUNT,
    NodeType.ARGMINCOUNT,
    NodeType.LESS,
    NodeType.GREATERCOUNT,
    NodeType.TOPN,
    NodeType.ENTITY
}

class SerializationFormat(Enum):
    HIERARCHICAL_DICT = "HIERARCHICAL_DICT"
    PREFIX_PARANTHESES = "PREFIX_PARANTHESES"
    TAG_SEQUENCE = "TAG_SEQUENCE"

def enum_for_str(key: str):
    for member in NodeType:
        if member.value == key:
            return member
    return None

class QueryTree:
    class Node:
        def __init__(self, type: NodeType, id: int = None, token: str = None):
            self.type: NodeType = type
            self.children: List[QueryTree.Node] = []
            self.id: int = id
            self.token: str = token
            self.kb_resources = []
        
        def collect(self, target_types: Set[NodeType]) -> list:
            return self.filter(lambda node: node.type in target_types)

        def filter(self, predicate) -> list:
            result = []
            if predicate(self):
                result.append(self)
            
            for child in self.children:
                result.extend(child.filter(predicate))
            
            return result

        def __str__(self):
            if self.type == NodeType.TOKEN:
                pretty_string = str(self.token)
            else: 
                pretty_string = self.type.value + '#{}'.format(abs(self.id))
            if self.kb_resources:
                kb_resources_text = ','.join([resource.split('/')[-1].replace('>', '') for resource in self.kb_resources])
                kb_resources_text = (kb_resources_text[:50] + '..') if len(kb_resources_text) > 50 else kb_resources_text 
                pretty_string += '[' + kb_resources_text + ']'
            return pretty_string 

    def __init__(self, root: Node, tokens: List[str], id: str = 'default'):
        self.last_id = -1
        def assign_unique_id(node):
            if node.id == None:
                node.id = self.last_id
                self.last_id -= 1

            for child in node.children:
                assign_unique_id(child)

        assign_unique_id(root)
        self.tokens = tokens
        self.root: Node = root
        self.unused_tokens = []
        self.id: str = id
   


        
    def to_serializable(self, format: SerializationFormat):
        '''
            This transforms the object to serializable types (dicts, lists, literals)
        '''
        if format == SerializationFormat.HIERARCHICAL_DICT:
            return self.to_dict()
        if format == SerializationFormat.PREFIX_PARANTHESES:
            def node2prefix(node):
                result = '(' + node.type.value
                for child in node.children:
                    result += ' ' + node2prefix(child)
                
                if node.type == NodeType.TOKEN:
                    result += ' ' + str(node.id)
                result += ')'
                return result
            return node2prefix(self.root)

    def to_dict(self) -> dict:
        def node_to_dict(node):
            node_dict = {}
            node_dict['type'] = node.type.value
            node_dict['id'] = node.id
            if node.children:
                node_dict['children'] = [node_to_dict(child) for child in node.children]
            
            if node.kb_resources:
                node_dict['kb_resources'] = node.kb_resources
            return node_dict
        
        return {
            'root': node_to_dict(self.root),
            'tokens': self.tokens,
            'id': self.id
        }

    def pretty_print(self):
        print(' '.join(self.tokens))
        print_tree(self.root, childattr='children')


    def offset_for_node(self, node: Node):
        tokens = [token.id for token in node.collect({NodeType.TOKEN})]
        begin_offset, end_offset = self._index_to_offset(tokens)

        return begin_offset, end_offset
    

    def text_for_node(self, node: Node) -> str:
        begin, end = self.offset_for_node(node)
        text = ' '.join(self.tokens)

        return text[begin:end]
        
    @classmethod
    def from_dict(cls, tree_dict: dict):
        tokens = tree_dict['tokens']
        token_nodes = [QueryTree.Node(NodeType.TOKEN, id, tokens[id]) for id in range(len(tokens))]
        used_nodes = set()
        
        def node_from_dict(tree_dict):
            node_type = enum_for_str(tree_dict['type'])

            if node_type == NodeType.TOKEN:
                node = token_nodes[tree_dict['id']]
                used_nodes.add(node)
            else:
                node = QueryTree.Node(node_type)
            
            if 'kb_resources' in tree_dict:
                node.kb_resources = tree_dict['kb_resources']

            if 'children' in tree_dict:
                for child in tree_dict['children']:
                    node.children.append(node_from_dict(child))
            
            return node

        def get_first_leaf(node: QueryTree.Node):
            if node.type == NodeType.TOKEN:
                return node.id
            else:
                return get_first_leaf(node.children[0])
        
        def sort_recursively(node: QueryTree.Node):
            for child in node.children:
                sort_recursively(child)
            node.children = sorted(node.children, key=lambda x: get_first_leaf(x))

        root = node_from_dict(tree_dict['root'])
        sort_recursively(root)
        example_id = tree_dict['id'] if 'id' in tree_dict else '0'
        tree = QueryTree(root, tokens, example_id)
        # Aggregate unused tokens 
        if len(used_nodes) < len(token_nodes):
            # unused_container_node = QueryTree.Node(NodeType.UNUSED)
            # root.children.append(unused_container_node)

            for node in token_nodes:
                if node not in used_nodes:
                    tree.unused_tokens.append(node)

                    # unused_container_node.children.append(node)
        
        return tree
    
    def find_parent(self, node: Node) -> Node:
        # TODO make this more efficient
        def find_parent_recursive(current_node, target_node):
            if target_node in current_node.children: return current_node
            
            for child in current_node.children:
                parent = find_parent_recursive(child, target_node)
                if parent: return parent
            
            return None
        return find_parent_recursive(self.root, node)
    
    def remove_children_of_type(self, node_type: NodeType):
        def remove_children_of_type_recursive(node, node_type):
            node.children = list(filter(lambda node: node.type != node_type, node.children))
            for child in node.children:
                remove_children_of_type_recursive(child, node_type)
        remove_children_of_type_recursive(self.root, node_type)

    def generate_relation_extraction_sequence(self, node: Node):
        '''
        Generate a relation extraction sequence for a relation node in the tree.
        '''
        # TODO this code does kind of the same thing as the query generation handlers. Make it dry
        # Also this is not the best place for this since it's grammar specific
        
        QUESTION_WORDS = {'who', 'when', 'what', 'how', 'which', 'list'}
        QUESTION_WORD_PAIRS = {'give me'}

        def offset_for_node_union(tree: QueryTree, nodes):
            union_begin, union_end = tree.offset_for_node(nodes[0])
            for node in nodes[1:]:
                node_begin, node_end = tree.offset_for_node(node)
                union_begin = min(union_begin, node_begin)
                union_end = max(union_end, node_end)
            return union_begin, union_end
            
        text = ' '.join(self.tokens)

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
            # e.g. Give me all [ENTITY] songs [/ENTITY] by [ENTITY] Bruce Springsteen [/ENTITY].
            e2_nodes = list(filter(lambda x: x.type in {NodeType.TYPE}, node.children))[:1] # TODO: currently only consider first type
        elif node.type in {NodeType.PROPERTYCONTAINS}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.ENTITY and x.type != NodeType.LITERAL, node.children))
            e2_nodes = list(filter(lambda x: x.type == NodeType.ENTITY or x.type == NodeType.LITERAL, node.children))
        elif node.type in {NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.ARGMAXCOUNT, NodeType.ARGMINCOUNT, NodeType.TOPN, NodeType.GREATERCOUNT}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.LITERAL, node.children))
            if len(e1_nodes) == 0: e1_nodes = list(filter(lambda x: x.type != NodeType.LITERAL, node.children))
        elif node.type in {NodeType.ISLESS, NodeType.ISGREATER}:
            # Technically there are 2 identical relations for each child entity. We only have to extract for one of them.
            e1_nodes = [node.children[0]]
        
        e1_begin, e1_end = offset_for_node_union(self, e1_nodes)

        if len(e2_nodes) == 0:
            first_word = self.tokens[0].lower()
            first_bigram = ' '.join(self.tokens[:2]).lower()
            if node.type == NodeType.PROPERTY and node in self.root.children and first_bigram in QUESTION_WORD_PAIRS:
                # We can consider the question word as one of the entities for the direct child of a root
                # e.g. [ENTITY] Who [/ENTITY] is the wife of [ENTITY] Barack Obama [/ENTITY] ?
                e2_begin = 0
                e2_end = len(first_bigram)
            elif node.type == NodeType.PROPERTY and node in self.root.children and first_word in QUESTION_WORDS:
                e2_begin = 0
                e2_end = len(first_word)
            else:
                # We only have one entity, so we add a dummy token before the e1 tokens
                new_token = ' [{}] '.format(node.type.value)
                sequence = sequence[:e1_begin] + new_token + sequence[e1_begin:]
                e2_begin, e2_end = e1_begin, e1_begin + len(new_token)
                e1_begin, e1_end = e1_begin + len(new_token), e1_end + len(new_token)
                # sequence = new_token + sequence
                # e2_begin, e2_end = 0, len(new_token)
                # e1_begin, e1_end = e1_begin + len(new_token), e1_end + len(new_token)
        else: 
            e2_begin, e2_end = offset_for_node_union(self, e2_nodes)

        result = {
            'text': sequence,
            'id': '{}${}'.format(self.id, node.id),
            'subject': sequence[e1_begin:e1_end],
            'object':sequence[e2_begin:e2_end],
            'subject_begin': e1_begin,
            'subject_end': e1_end,
            'object_begin': e2_begin,
            'object_end': e2_end,
        }

        if len(node.kb_resources) > 0:
            result['relation'] = node.kb_resources[0]

        return result

    def _index_to_offset(self, token_indexes: List[int]) -> (int, int):
        '''
            Convertor from token index clusters to begin-end offset notation.
            E.g. Who is the wife of Barack Obama?
            input: [0]
            output: (0,3)
        '''
        token_indexes = sorted(token_indexes)
        text = ' '.join(self.tokens)

        target_text  = ' '.join(self.tokens[token_indexes[0]:token_indexes[-1] + 1])
        target_begin = text.find(target_text)
        target_end    = target_begin + len(target_text)

        return (target_begin, target_end)