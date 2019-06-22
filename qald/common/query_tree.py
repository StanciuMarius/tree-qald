import os
import sys
sys.path.insert(0, os.getcwd())

from enum import Enum
from typing import List

class NodeType(Enum):
    # The answer of a query
    ROOT = 'ROOT'
    
    # Computes the cardinal of a set of entities
    COUNT = 'COUNT'

    # Picks the entity from a set with the highest value for a particular relation (to be extracted)
    ARGMAX = 'ARGMAX'

    # Picks the entity from a set with the lowest value for a particular relation (to be extracted)
    ARGMIN = 'ARGMIN'

    # Picks the entity from a set with the n-th lowest value (to be extracted)
    ARGNTH = 'ARGNTH'

    # Returns true if the given set is not empty
    EXISTS = 'EXISTS'

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

    # Property of a set of a entities
    PROPERTY = 'PROPERTY'

    # Tokens that represent knowledge base TYPE+. E.g. "comonauts" "writer" 
    TYPE = 'TYPE'

    # Tokens that represent knowledge base entities. E.g. "Barack Obama", "Titanic"
    ENTITY = 'ENTITY'

    # Tokens that represent literals. E.g. "100", "15th of June", "1999", "1.0", "Frank the Tank"
    LITERAL = 'LITERAL'
    
    # All entities of a particular type

    ENUMERATE = 'ENUMERATE'
    
    # Unused tokens
    UNUSED = 'UNUSED'

    # WH-words
    VARIABLE = 'VARIABLE'

    # A token
    TOKEN = 'TOKEN'
    
    # Lists
    TYPES = 'TYPE+'
    ENTITIES = 'ENTITY+'
    SUBJECTS = 'SUBJECT+'
    OBJECTS = 'OBJECT+'
    TOKENS = 'TOKEN+'

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
        
        def __str__(self):
            pretty_string = self.type.value
            if self.type == NodeType.TOKEN:
                pretty_string += '(' + str(self.token) + ')'
            return pretty_string 

    def __init__(self, root: Node, tokens: List[str]):
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
                
            return node_dict
        
        return node_to_dict(self.root)

    @classmethod
    def from_dict(cls, tree_dict: dict, tokens: List[str]):
        token_nodes = [QueryTree.Node(NodeType.TOKEN, id, tokens[id]) for id in range(len(tokens))]
        used_nodes = set()
        
        def node_from_dict(tree_dict):
            node_type = enum_for_str(tree_dict['type'])

            if node_type == NodeType.TOKEN:
                node = token_nodes[tree_dict['index']]
                used_nodes.add(node)
            else:
                node = QueryTree.Node(node_type)

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

        root = node_from_dict(tree_dict)
        sort_recursively(root)
            
        tree = QueryTree(root, tokens)
        # Aggregate unused tokens 
        if len(used_nodes) < len(token_nodes):
            # unused_container_node = QueryTree.Node(NodeType.UNUSED)
            # root.children.append(unused_container_node)

            for node in token_nodes:
                if node not in used_nodes:
                    tree.unused_tokens.append(node)

                    # unused_container_node.children.append(node)
        
        return tree