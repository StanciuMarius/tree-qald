import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree
from common.query_tree import SerializationFormat

def parse(tokens: List[str]) -> QueryTree:
    '''
    Not implemented yet. Returns dummy tree
    '''
    tree_dict = {
        'type': 'ROOT',
        'children': [
            {
                'type': 'QUERY',
                'children': [
                    {
                        'type': 'QUERY',
                        'children': [
                            {
                                'type': 'ENTITY',
                                'children': [
                                    {
                                        'type': 'TOKEN',
                                        'index': 1
                                    },
                                    {
                                        'type': 'TOKEN',
                                        'index': 2
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'type': 'RELATION',
                        'children': [
                            {
                                'type': 'TOKEN',
                                'index': 4
                            },
                            {
                                'type': 'TOKEN',
                                'index': 5
                            }
                        ]
                    }
                ]
            }
        ]
    }
    tree = QueryTree.from_dict(tree_dict, tokens)
    return tree