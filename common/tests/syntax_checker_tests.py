import unittest
import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree
from services.parser.constants import GRAMMAR_FILE_PATH
from common.syntax_checker import SyntaxChecker

class TestSyntaxChecker(unittest.TestCase):
    def test_correct_tree_1(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'root': {
                'type': 'ROOT',
                'children': [
                    {
                        'type': 'COUNT',
                        'children': [
                            {
                                'type': 'PROPERTY',
                                'children': [
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 1
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 2
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'tokens': ['a', 'b', 'c', 'd', 'e', 'f']
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertTrue(checker.validate(query_tree))

    def test_correct_tree_2(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'root': {
                'type': 'ROOT',
                'children': [
                    {
                        'type': 'ARGMAX',
                        'children': [
                            {
                                'type': 'PROPERTY',
                                'children': [
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 1
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 2
                                            }
                                        ]
                                    },
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 3
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 4
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'tokens': ['a', 'b', 'c', 'd', 'e', 'f']
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertTrue(checker.validate(query_tree))

    def test_correct_tree_3(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'root': {
                'type': 'ROOT',
                'children': [
                    {
                        'type': 'ISA',
                        'children': [
                        {
                            'type': 'ARGMAX',
                            'children': [
                                {
                                'type': 'PROPERTY',
                                'children': [
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 1
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 2
                                            }
                                        ]
                                    }
                                ]
                                } 
                            ]
                        },
                         {
                            'type': 'TYPE',
                            'children': [
                                {
                                    'type': 'TOKEN',
                                    'id': 4
                                },
                                {
                                    'type': 'TOKEN',
                                    'id': 5
                                }
                            ]
                        } 
                        ]  
                            
                    }
                ]
            },
            'tokens': ['a', 'b', 'c', 'd', 'e', 'f']
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertTrue(checker.validate(query_tree))

    def test_correct_tree_4(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'root': {
                'type': 'ROOT',
                'children': [
                    {
                        'type': 'ISA',
                        'children': [
                            {
                                'type': 'PROPERTY',
                                'children': [
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 1
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 2
                                            }
                                        ]
                                    },
                                    {
                                        'type': 'ENTITY',
                                        'children': [
                                            {
                                                'type': 'TOKEN',
                                                'id': 3
                                            },
                                            {
                                                'type': 'TOKEN',
                                                'id': 4
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'tokens': ['a', 'b', 'c', 'd', 'e', 'f']
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertFalse(checker.validate(query_tree))
if __name__ == '__main__':
    unittest.main()
