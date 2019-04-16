import os
import sys

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree
from common.query_tree import SerializationFormat



def parse(question_text: str) -> QueryTree:
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
                                        'type': 'TOKENS',
                                        'tokens': [1, 2]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'type': 'RELATION',
                        'children': [
                            {
                                'type': 'TOKENS',
                                'tokens': [2, 3]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    tree = QueryTree.from_dict(tree_dict)
    return tree

