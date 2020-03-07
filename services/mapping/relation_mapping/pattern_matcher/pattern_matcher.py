import os
import sys
import spacy
import re
import base64
from tqdm import tqdm
from typing import List

sys.path.insert(0, os.getcwd())

from services.tasks import run_task, Task
from services.mapping.constants import PATTY_DBPEDIA_PARAPHRASES_FILE_PATH, PATTY_POS_VS_SPACY_POS

class PattyPatternTrie:
    class Node:    
        def __init__(self):
            self.children = {}
            self.values = []
    
        def add_child(self, key: str):
            if key not in self.children:
                node = PattyPatternTrie.Node()
                self.children[key] = node
            else:
                node = self.children[key]
            return node
        
        def get_child(self, key: str):
            if key in self.children:
                return self.children[key]
            else:
                return None

        def add_value(self, value):
            self.values.append(value)

    
    def __init__(self, pattern_file_path: str):
        self.root = PattyPatternTrie.Node()
        self.stop_words = {'is'}
        with open(pattern_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()[1:]

        for line in tqdm(lines, desc='Loading PATTY pattern trie'):
            relation, pattern_string = line.split('\t')
            pattern_string = pattern_string.strip()
            if pattern_string[-1] == ';':
                pattern_string = pattern_string[:-1]

            pattern_tokens = pattern_string.split(' ')

            self.__add_pattern(pattern_tokens, relation)

    def __add_pattern(self, tokens: List[str], relation):
        it = self.root
        for i, token in enumerate(tokens):
            if token in PATTY_POS_VS_SPACY_POS:
                token = PATTY_POS_VS_SPACY_POS[token]
            it = it.add_child(token)
        
        it.add_value(relation)

    def get_value(self, tokens: List[str], pos_tags: List[str]):
        def get_value_recursive(root: PattyPatternTrie.Node, tokens: List[str], pos_tags: List[str], index: int, key: str, matches: List[str]):
            # Check if last token, return the value
            if index == len(tokens):
                matches.extend(root.values)
                return

            token = tokens[index]
            pos_tag = pos_tags[index]
            
            # The sentence can either match on the word or on the words' POS tag
            pos_child = root.get_child(pos_tag)
            token_child = root.get_child(token)

            val = None

            # Match on POS tag
            if pos_child is not None:
                get_value_recursive(pos_child, tokens, pos_tags, index + 1, key + ' ' + pos_tag, matches)
            # Match on token
            if token_child is not None:
                get_value_recursive(token_child, tokens, pos_tags, index + 1, key + ' ' + token, matches)
            # Skip stop-words
            if token in self.stop_words:
                get_value_recursive(root, tokens, pos_tags, index + 1, key, matches)

        matches = []
        get_value_recursive(self.root, tokens, pos_tags, 0, "", matches)
        return matches

            
class RelationPatternMatcher:

    def __init__(self, pattern_file_path: str):
        self.pattern_trie = PattyPatternTrie(pattern_file_path)
    
    def find_relation(self, question_text, subject_begin, subject_end, object_begin, object_end):
        if subject_begin < object_begin:
            text_between_begin = subject_end
            text_between_end = object_begin
            is_reversed = False
        else:
            text_between_begin = object_end
            text_between_end = subject_begin
            is_reversed = True

        info = run_task(Task.SPACY_PROCESS, question_text)
        tokens = info['tokens']
        idx = info['idx']
        pos = info['pos']

        between_token_indexes = self.__tokens_in_range(tokens, text_between_begin, text_between_end, idx)
        between_token_indexes = list(filter(lambda i: pos[i] != 'PUNCT', between_token_indexes))
        
        between_tokens = [tokens[i] for i in between_token_indexes]
        between_pos    = [pos[i]    for i in between_token_indexes]
        
        between_text = ' '.join(between_tokens)


        # try:
        candidate = self.pattern_trie.get_value(between_tokens, between_pos)
        # except:
            # candidate = None
        
        return (candidate, between_text)
    
    
    def __tokens_in_range(self, tokens, lower_bound, upper_bound, idx):
        return [i for i in range(len(tokens)) if idx[i] >= lower_bound and idx[i] < upper_bound]

