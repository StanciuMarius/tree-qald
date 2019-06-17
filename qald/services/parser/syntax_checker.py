
from functools import reduce

import os
import sys
from copy import deepcopy
sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, enum_for_str, NodeType
COLLAPSABLE_NODES = {
    NodeType.ENTITY: NodeType.ENTITIES,
    NodeType.TOKEN: NodeType.TOKENS,
    NodeType.TYPE: NodeType.TYPES,
    NodeType.SUBJECT: NodeType.SUBJECTS,
    NodeType.OBJECT: NodeType.OBJECTS,
}
class SyntaxChecker:
    """ Tool for checking the syntax of QueryTrees against a context free grammar file """
    def __init__(self, grammar_file_path: str):
        # Baseline tree-like dict for syntax checking
        self.grammar = {}
        self.sorting_rule = key=lambda t: t.value # for pattern matching

        with open(grammar_file_path, 'r') as grammar_file:
            for line in grammar_file.readlines():
                trimmed = line.strip()
                
                # Skip comment
                if len(trimmed) > 1 and trimmed[0] == '#':
                    continue
                
                if len(line) > 2:
                    non_terminal, alternatives = line.split(":")
                    non_terminal = non_terminal.replace(' ',  '').replace('\n', '')

                    # Parsin' trimmin' validatin'
                    alternatives = alternatives.split("|")
                    alternatives = [[symbol.replace(' ',  '').replace('\n', '') for symbol in alternative.split(' ')] for alternative in alternatives]
                    alternatives = [[symbol for symbol in symbols if symbol] for symbols in alternatives]
                    

                    # Expand optional
                    def expand_backtrack(symbols):
                        if not symbols:
                            return [[]]
                        
                        expanded_symbols = []
                        alternatives = expand_backtrack(symbols[1:])

                        if symbols[0][-1] == '?':
                            # if optional, skip
                            expanded_symbols.extend(alternatives)
                            expanded_symbols.extend([[symbols[0][:-1]] + alternative for alternative in alternatives])
                        else:
                            expanded_symbols.extend([[symbols[0]] + alternative for alternative in alternatives])

                        return deepcopy(expanded_symbols)
                        
                    expanded_alternatives = []
                    for symbols in alternatives:
                        expanded_alternatives.extend(expand_backtrack(symbols))
                    expanded_alternatives = [tuple([enum_for_str(symbol) for symbol in symbols]) for symbols in expanded_alternatives]

                    self.grammar[enum_for_str(non_terminal)] = expanded_alternatives

    def validate(self, tree: QueryTree) -> bool:
        """ Checks the syntax of a QueryTree against the grammar passed to the constructor """

        return self.__check_query_node(tree.root)

    
    def __check_query_node(self, node: QueryTree.Node):
        # Terminals are fine
        if node.type is NodeType.TOKEN:
            return True
        
        # Unknown symbol
        if node.type not in NodeType or node.type not in self.grammar:
            return False
        
        
        children_symbols = tuple(sorted([child.type for child in node.children], key=self.sorting_rule))


        # Collapse lists
        collapsed_children_symbols = tuple(sorted(set([child.type for child in node.children]), key=self.sorting_rule))
        collapsed_children_symbols = tuple([COLLAPSABLE_NODES[node_type] if node_type in COLLAPSABLE_NODES else node_type for node_type in collapsed_children_symbols])

        allowed_alternatives = self.grammar[node.type]
        
        # Node childrens match the rule for that particular type
        if children_symbols in allowed_alternatives:
            return reduce(lambda a, x: a and self.__check_query_node(x), node.children, True)

        # Also try list versions
        if collapsed_children_symbols in allowed_alternatives:
            return reduce(lambda a, x: a and self.__check_query_node(x), node.children, True)

        return False