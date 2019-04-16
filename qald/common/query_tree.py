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

class SerializationFormat(Enum):
    OBJECT_ORIENTED = "OBJECT_ORIENTED"
    ADJECENCY = "ADJECENCY"

def enum_for_str(key: str):
    for member in NodeType:
        if member.value == key:
            return member
    return None

class QueryTree:
    class Node:
        def __init__(self, type: NodeType, tokens: List[int] = []):
            self.type: NodeType = type
            self.tokens: List[int] = tokens
            self.children: List[QueryTree.Node] = []
            self.id: int = -1
    def __init__(self, root: Node):
        self.last_id = 0
        def generate_unique_ids(node):
            node.id = self.last_id
            self.last_id += 1
            for child in node.children:
                generate_unique_ids(child)

        generate_unique_ids(root)

        self.root: Node = root
   

    def to_serializable(self, format: SerializationFormat):
        if format == SerializationFormat.OBJECT_ORIENTED:
            return self.to_dict()
        elif format == SerializationFormat.ADJECENCY:
            def to_dict_recursive(node: QueryTree.Node, nodes: List[dict], edges: List[dict]):

                nodes.append({
                    'id': node.id,
                    'label': node.type.value
                })

                for child in node.children:
                    to_dict_recursive(child, nodes, edges)
                    edges.append({
                        'from': node.id,
                        'to': child.id
                    })

            nodes = []
            edges = []

            to_dict_recursive(self.root, nodes, edges)

            tree = {
                'nodes': nodes,
                'edges': edges
            }

            return tree
            
    def to_dict(self) -> dict:
        def to_dict_recursive(node: QueryTree.Node):
            node_dict = {}
            node_dict['type'] = node.type.value
            if node.tokens:
                node_dict['tokens'] = node.tokens
            if node.children:
                node_dict['children'] = [to_dict_recursive(child) for child in node.children]
            
            return node_dict
        
        return to_dict_recursive(self.root)


    @classmethod
    def from_dict(cls, tree_dict: dict):
        def node_from_dict(tree_dict):
            node_type = enum_for_str(tree_dict['type'])
            node = QueryTree.Node(node_type)
            if node_type == NodeType.TOKENS:
                node.tokens = tree_dict['tokens']
            
            if 'children' in tree_dict:
                for child in tree_dict['children']:
                    node.children.append(node_from_dict(child))
            
            return node
            
        tree = QueryTree(node_from_dict(tree_dict))
        return tree