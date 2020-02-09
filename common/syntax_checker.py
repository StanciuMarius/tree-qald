
from functools import reduce

import os
import sys
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, enum_for_str, NodeType
import copy


class SyntaxChecker:
    """ Tool for checking the syntax of QueryTrees against a context free grammar file """
    def __init__(self, grammar_file_path: str):
        # Baseline tree-like dict for syntax checking
        self.grammar = {}
        self.rule_vs_alias = {}

        self.sorting_rule = key=lambda t: t.value # for pattern matching

        with open(grammar_file_path, 'r') as grammar_file:
            lines = grammar_file.readlines()
            # =========================================Parse aliases
            for line in lines:
                trimmed = line.strip()
                
                # Skip comment
                if len(trimmed) > 1 and trimmed[0] == '#':
                    continue

                if len(line) > 2:

                    non_terminal, _ = line.split(":")
                    non_terminal = non_terminal.replace(' ',  '').replace('\n', '').split('$')
                    alias = None
                    if len(non_terminal) > 1:
                        non_terminal, alias = non_terminal
                    else:
                        non_terminal = non_terminal[0]

                    if alias:
                        self.rule_vs_alias[non_terminal] = alias
        
            for line in lines:
                trimmed = line.strip()
                
                # Skip comment
                if len(trimmed) > 1 and trimmed[0] == '#':
                    continue

                if len(line) > 2:

                    non_terminal, alternatives = line.split(":")
                    non_terminal = non_terminal.replace(' ',  '').replace('\n', '').split('$')[0]

                    # Parsin' trimmin' validatin'
                    alternatives = alternatives.split("|")
                    alternatives = [[symbol.replace(' ',  '').replace('\n', '') for symbol in alternative.split(' ')] for alternative in alternatives]
                    alternatives = [[symbol for symbol in symbols if symbol] for symbols in alternatives]

                    self.grammar[non_terminal] = alternatives

    def validate(self, tree: QueryTree) -> bool:
        """ Checks the syntax of a QueryTree against the grammar passed to the constructor """
        try:
            return self.__check_query_node(tree.root)
        except:
            return False

    
    def __check_query_node(self, node: QueryTree.Node):
        # Terminals are fine
        if node.type is NodeType.TOKEN:
            return True
        
        # Unknown symbol
        if node.type not in NodeType or node.type.value not in self.grammar:
            return False

        found_valid_alternative = False
        for alternative in self.grammar[node.type.value]:
            alternative = copy.copy(alternative)
            children = copy.copy(node.children)
            
            non_empty_lists = set()
            symbols_satisfied = True
            for child in children:
                alias = self.rule_vs_alias[child.type.value] if child.type.value in self.rule_vs_alias else ''
                if child.type.value in alternative:
                    alternative.remove(child.type.value)
                elif alias in alternative:
                    alternative.remove(alias)
                elif child.type.value + '+' in alternative:
                    non_empty_lists.add(child.type.value + '+')
                elif alias + '+' in alternative:
                    non_empty_lists.add(alias + '+')
                elif child.type.value + '*' not in alternative and alias + '*' not in alternative:
                    symbols_satisfied = False
            
            # There should only be non-empty +lists or *lists
            lists_satisfied = True
            for symbol in alternative:
                if not ('*' in symbol) and not ('+' in symbol and symbol in non_empty_lists):
                    lists_satisfied = False
            
            if symbols_satisfied and lists_satisfied:
                found_valid_alternative = True
                break

        # Recurse syntax check to children
        return found_valid_alternative and reduce(lambda result, child: result and self.__check_query_node(child), node.children, True)