import os
import sys
sys.path.insert(0, os.getcwd())

from enum import Enum
from typing import List

class NodeType(Enum):
    # The answer of a query
    ROOT = 'ROOT'
    
    # Compares two entities. The order is given by the token order in the questions.
    COMPARE = 'COMPARE'

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

    # Returns true if the type of the given entity matches the given type
    ISA = 'ISA'

    # Filters the entities with a relation value (to be extracted) greater than a given value
    GREATER = 'GREATER'

    # Filters the entities with a relation value (to be extracted) less than a given value
    LESS = 'LESS'

    # The subject of a triple. Has at least an object associated with it. Can have TYPE+. Can have a variable (for relation extraction purposes)
    SUBJECT = 'SUBJECT'

    # The object of a triple. Has at least a subject associated with it. Can have TYPE+. Can have a variable (for relation extraction purposes)
    OBJECT = 'OBJECT'

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
    
    # Lists
    TYPES = 'TYPE+'
    ENTITIES = 'ENTITY+'
    SUBJECTS = 'SUBJECT+'
    OBJECTS = 'OBJECT+'
    TOKENS = 'TOKEN+'

class SerializationFormat(Enum):
    HIERARCHICAL_DICT = "HIERARCHICAL_DICT"
    PREFIX_PARANTHESES = "PREFIX_PARANTHESES"

def enum_for_str(key: str):
    for member in NodeType:
        if member.value == key:
            return member
    return None

class QueryTree:
    class Node:
        def __init__(self, type: NodeType, id: int = None):
            self.type: NodeType = type
            self.children: List[QueryTree.Node] = []
            self.id: int = id

    def __init__(self, root: Node, tokens: List[str]):
        self.last_id = -1
        def assign_unique_id(node):
            if not node.id:
                node.id = self.last_id
                self.last_id -= 1

            for child in node.children:
                assign_unique_id(child)

        assign_unique_id(root)
        self.tokens = tokens
        self.root: Node = root
        self.unused_tokens = []
   

    def to_serializable(self, format: SerializationFormat):
        if format == SerializationFormat.HIERARCHICAL_DICT:
            return self.to_dict()
        if format == SerializationFormat.PREFIX_PARANTHESES:
            def node2prefix(node):
                result = '(' + node.type.value
                for child in node.children:
                    result += ' ' + node2prefix(child)
                
                if node.type == NodeType.TOKEN:
                    result += ' ' + self.tokens[node.id] 
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
        token_nodes = [QueryTree.Node(NodeType.TOKEN, id) for id in range(len(tokens))]
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

        root = node_from_dict(tree_dict)

            
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