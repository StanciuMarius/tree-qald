import json
import numpy as np
from typing import List
import torch
import os
import sys
import re

sys.path.insert(0, os.getcwd())

from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from datasets.relation_extraction.cross_kb_relations.resolver import EquivalentRelationResolver
import services.mapping.relation_mapping.relation_classifier.constants as constants
import common.knowledge_base as knowledge_base

UNKNOWN_LABEL = 'UNKNOWN'

class NormalizeRelationUriTransofrm(object):
    def __call__(self, sample):
        relation_uri = sample['relation']

        relation_uri = relation_uri.replace('www.', '')
        if not relation_uri.startswith('http://') and 'tacred:' not in relation_uri and 'qald:' not in relation_uri and relation_uri != 'NA':
            relation_uri = 'http://' + relation_uri
        relation_uri = relation_uri.replace('http://rdf.freebase.com/ns/', 'http://freebase.com/').replace('https', 'http')
        sample['relation'] = relation_uri
        return sample

class BertRelationExtractionFormatTransform(object):
    def __call__(self, sample):
        text = sample['text']
        subject_begin = sample['subject_begin']
        subject_end = sample['subject_end']
        object_begin = sample['object_begin']
        object_end = sample['object_end']

        if subject_begin >= 0 and subject_end <= len(text) and subject_begin <= subject_end:
            new_token_indices = [
                ('[ENTITY]', subject_begin),
                ('[/ENTITY]', subject_end),
            ]
        if object_begin >= 0 and object_end <= len(text) and object_begin <= object_end:
            new_token_indices.extend([
                ('[ENTITY]', object_begin),
                ('[/ENTITY]', object_end)
            ])
        
        new_token_indices = sorted(new_token_indices, key=lambda x: x[1])
        accumulated_offset = 0
        for token, old_index in new_token_indices:
            text_to_insert = ' ' + token + ' '
            new_index = old_index + accumulated_offset
            text = text[:new_index] + text_to_insert + text[new_index:]
            accumulated_offset += len(text_to_insert)
        result = {'text': text}
        if 'label' in sample:
            result['relation'] = sample['label']
        return result

class EquivalentRelationTransform(object):
    def __init__(self, save_statistics=False):
        self.resolver = EquivalentRelationResolver()
        self.save_statistics = save_statistics
        if save_statistics:
            self.unknown_relations = {}
            self.unknown_relation_count = 0

    def __call__(self, sample, kb: knowledge_base.KnowledgeBase=None):
        relation = sample['relation']
        generic_relation = self.resolver(relation, kb)

        # Undirectional classification so we remove reverse relation labels
        if generic_relation and generic_relation[0] == '_': generic_relation = generic_relation[1:]

        if generic_relation:
            sample['label'] = generic_relation
        else:
            sample['label'] = UNKNOWN_LABEL
            if self.save_statistics:
                self.unknown_relation_count += 1
                new_count = (1 if relation not in self.unknown_relations else self.unknown_relations[relation][0] + 1, sample['text'])
                self.unknown_relations[relation] = new_count

        return sample


def has_unknown_relation(example):
    return example['relation'] == UNKNOWN_LABEL

def has_na_relation(example):
    return example['relation'] == 'NA'

def is_valid_bert_sequence(example):
    text = example['text']
    starts = len(list(re.finditer('\[ENTITY\]', text)))
    ends = len(list(re.finditer('\[/ENTITY\]', text)))
    return  starts == 2 and ends == 2

def has_less_than_n_tokens(example):
    return len(example['text'].split(' ')) < constants.MAX_SEQUENCE_LENGTH   

def validate(example, statistics=None):
    unknown_relation = has_unknown_relation(example)
    na_relation = has_na_relation(example)
    invalid_bert_sequence = not is_valid_bert_sequence(example)
    has_more_than_n_tokens = not has_less_than_n_tokens(example)
    is_valid = not unknown_relation and not na_relation and not invalid_bert_sequence and not has_more_than_n_tokens
    if statistics is not None:
        if 'unknown_relation' not in statistics: statistics['unknown_relation'] = 0
        if 'na_relation' not in statistics: statistics['na_relation'] = 0
        if 'invalid_bert_sequence' not in statistics: statistics['invalid_bert_sequence'] = 0
        if 'has_more_than_n_tokens' not in statistics: statistics['has_more_than_n_tokens'] = 0
        if 'is_valid' not in statistics: statistics['is_valid'] = 0

        if unknown_relation: statistics['unknown_relation'] += 1
        if na_relation: statistics['na_relation'] += 1
        if invalid_bert_sequence: statistics['invalid_bert_sequence'] += 1
        if has_more_than_n_tokens: statistics['has_more_than_n_tokens'] += 1
        if is_valid: statistics['is_valid'] += 1

    return is_valid
