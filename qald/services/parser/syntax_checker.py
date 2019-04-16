
from functools import reduce

import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, enum_for_str, NodeType

class SyntaxChecker:
    """ Tool for checking the syntax of QueryTrees against a context free grammar file """
    def __init__(self, grammar_file_path: str):
        # Baseline tree-like dict for syntax checking
        self.grammar = {}
        self.sorting_rule = key=lambda t: t.value # for pattern matching

        with open(grammar_file_path, 'r') as grammar_file:
            for line in grammar_file.readlines():
                if len(line) > 2:
                    non_terminal, alternatives = line.split(":")

                    non_terminal = non_terminal.replace(' ',  '').replace('\n', '')

                    # Parsin' trimmin' validatin'
                    alternatives = alternatives.split("|")
                    alternatives = [[symbol.replace(' ',  '').replace('\n', '') for symbol in alternative.split(' ')] for alternative in alternatives]
                    
                    alternatives = [[enum_for_str(symbol) for symbol in symbols if symbol] for symbols in alternatives]
                    alternatives = [tuple(sorted(symbols, key=self.sorting_rule)) for symbols in alternatives]
                    self.grammar[enum_for_str(non_terminal)] = alternatives

    def validate(self, tree: QueryTree) -> bool:
        """ Checks the syntax of a QueryTree against the grammar passed to the constructor """

        return self.__check_query_node(tree.root)
    

    
    def __check_query_node(self, node: QueryTree.Node):
        # Terminals are fine
        if node.type is NodeType.TOKENS:
            return True
        
        # Unknown symbol
        if node.type not in NodeType or node.type not in self.grammar:
            return False
        
        
        children_symbols = tuple(sorted([child.type for child in node.children], key=self.sorting_rule))
        allowed_alternatives = self.grammar[node.type]
        
        # Node childrens match the rule for that particular type
        if children_symbols in allowed_alternatives:
            return reduce(lambda a, x: a and self.__check_query_node(x), node.children, True)

        return False