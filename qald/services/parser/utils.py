from typing import Set
import json
import os
import sys

from pptree import print_tree
sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree, NodeType, SerializationFormat


def contains_any(question: QueryTree, target: Set[NodeType]):
    def contains_node_in_set_recursive(node: QueryTree.Node, target: Set[NodeType]):
        if node.type in target:
            return True
        else:
            for child in node.children:
                if contains_node_in_set_recursive(child, target):
                    return True
        
        return False

    return contains_node_in_set_recursive(question.root, target)


def contains_bad_exists(question: QueryTree):
    def containts_bad_exists_recursive(node: QueryTree.Node):
        if node.type == NodeType.PROPERTY and len(node.children) == 2 and node.children[0].type == NodeType.ENTITY and node.children[1].type == NodeType.ENTITY:
            return True
        else:
            for child in node.children:
                if containts_bad_exists_recursive(child):
                    return True
        
        return False

    return containts_bad_exists_recursive(question.root)



