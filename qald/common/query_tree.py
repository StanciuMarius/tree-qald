import os
import sys
sys.path.insert(0, os.getcwd())

from enum import Enum
from typing import List


class NodeType(Enum):
    ROOT = "ROOT"
    QUERY = "QUERY"
    COMPARE = "COMPARE"
    RELATION_EXISTS = "RELATION_EXISTS"
    INTERSECTION = "INTERSECTION"
    EXISTS = "EXISTS"
    UNION = "UNION"
    COUNT = "COUNT"
    EQUAL = "EQUAL"
    ARGMAX = "ARGMAX"
    ENTITY = "ENTITY"
    TYPE = "TYPE"
    RELATION = "RELATION"
    TOKENS = "TOKENS"
    TOKEN = "TOKEN"
    VOID = "VOID"
    ARGNTH = "ARGNTH"
    ISA = "ISA"
    
    FILTER = "FILTER"
    CONDITION = "CONDITION"
    GREATER = "GREATER"

    UNUSED = "UNUSED"

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

        # Aggregate unused tokens 
        if len(used_nodes) < len(token_nodes):
            unused_container_node = QueryTree.Node(NodeType.UNUSED)
            root.children.append(unused_container_node)

            for node in token_nodes:
                if node not in used_nodes:
                    unused_container_node.children.append(node)
        
            
        tree = QueryTree(root, tokens)
        return tree