import unittest
import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree
from services.parser.constants import GRAMMAR_FILE_PATH
from services.parser.syntax_checker import SyntaxChecker

class TestSyntaxChecker(unittest.TestCase):
    def test_correct_tree_1(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
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
                            'type': 'PROPERTY',
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

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertTrue(checker.check_syntax(query_tree))

    def test_correct_tree_2(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'type': 'ROOT',
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
                                },
                                {
                                    'type': 'TYPE',
                                    'children': [
                                    {
                                        'type': 'TOKENS',
                                        'tokens': [1, 2]
                                    },
                                    ]
                                },
                            ]
                        },
                    ]
                }
            ]
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertTrue(checker.check_syntax(query_tree))

    def test_incorrect_tree_1(self):
        checker = SyntaxChecker(GRAMMAR_FILE_PATH)
        tree_dict = {
            'type': 'ROOT',
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
                        },
                        {
                            'type': 'TYPE',
                            'children': [
                                {
                                    'type': 'TOKENS',
                                    'tokens': [1, 2]
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        query_tree = QueryTree.from_dict(tree_dict)
        self.assertFalse(checker.check_syntax(query_tree))

if __name__ == '__main__':
    unittest.main()
