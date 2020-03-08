import json
import numpy as np
from typing import List
import torch

from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from common.syntax_checker import SyntaxChecker
from common.constants import GRAMMAR_FILE_PATH
from datasets.relation_extraction.cross_kb_relations.resolver import EquivalentRelationResolver
import common.knowledge_base as knowledge_base
UNKNOWN_LABEL = 'UNKNOWN'
SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)
QUESTION_WORDS = {'who', 'when', 'what', 'how', 'which'}

class NormalizeRelationUriTransofrm(object):
    def __call__(self, sample):
        relation_uri = sample['relation']

        relation_uri = relation_uri.replace('www.', '')
        if not relation_uri.startswith('http://') and 'tacred:' not in relation_uri and 'qald:' not in relation_uri:
            relation_uri = 'http://' + relation_uri
        relation_uri = relation_uri.replace('http://rdf.freebase.com/ns/', 'http://freebase.com/').replace('https', 'http')
        sample['relation'] = relation_uri
        return sample

class BertRelationExtractionFormatTransform(object):
    def __call__(self, sample):
        text = sample['text']
        new_token_indices = [
            ('[E1]', sample['subject_begin']),
            ('[/E1]', sample['subject_end']),
            ('[E2]', sample['object_begin']),
            ('[/E2]', sample['object_end']),
        ]
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

def has_valid_bert_sequence(example):
    text = example['text']
    return '[E1]' in text and '[/E1]' in text and '[E2]' in text and '[/E2]' in text and len(text.split(' ')) < 450   

def validate(example):
    return not has_unknown_relation(example) and not has_na_relation(example) and has_valid_bert_sequence(example)
    
def generate_relation_extraction_sequences(tree: QueryTree):    
    def offset_for_node_union(tree: QueryTree, nodes):
        union_begin, union_end = tree.offset_for_node(nodes[0])
        for node in nodes[1:]:
            node_begin, node_end = tree.offset_for_node(node)
            union_begin = min(union_begin, node_begin)
            union_end = max(union_end, node_end)
        return union_begin, union_end

    text = ' '.join(tree.tokens)
    relation_nodes = tree.root.collect(RELATION_NODE_TYPES)

    node_vs_sequence = {}

    for node in relation_nodes:
        if len(node.kb_resources) == 0:
            continue
        # Generate one sequence for each relation node
        sequence = text

        e1_nodes = []
        e2_nodes = []

        if node.type in {NodeType.EXISTSRELATION}:
            # Relation is between 2 entities/literal
            e1_nodes = [node.children[0]]
            e2_nodes = [node.children[1]]
        elif node.type in {NodeType.GREATER, NodeType.LESS}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.LITERAL, node.children))
            e2_nodes = list(filter(lambda x: x.type in {NodeType.LITERAL}, node.children))
        elif node.type in {NodeType.PROPERTY}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE, node.children))
            # We can consider a type as a substitute for entities
            # e.g. Give me all [E1] songs [/E1] by [E2] Bruce Springsteen [/E2].
            e2_nodes = list(filter(lambda x: x.type in {NodeType.TYPE}, node.children))[:1] # TODO: currently only consider first type
        elif node.type in {NodeType.PROPERTYCONTAINS}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.ENTITY and x.type != NodeType.LITERAL, node.children))
            e2_nodes = list(filter(lambda x: x.type == NodeType.ENTITY or x.type == NodeType.LITERAL, node.children))
        elif node.type in {NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.ARGMAXCOUNT, NodeType.ARGMINCOUNT, NodeType.TOPN, NodeType.GREATERCOUNT}:
            e1_nodes = list(filter(lambda x: x.type != NodeType.TYPE and x.type != NodeType.LITERAL, node.children))
            if len(e1_nodes) == 0: e1_nodes = list(filter(lambda x: x.type != NodeType.LITERAL, node.children))
        elif node.type in {NodeType.ISLESS, NodeType.ISGREATER}:
            # Technically there are 2 identical relations for each child entity. We can only extract for one of them.
            e1_nodes = [node.children[0]]
        
        e1_begin, e1_end = offset_for_node_union(tree, e1_nodes)

        if len(e2_nodes) == 0:
            if node.type == NodeType.PROPERTY and tree.tokens[0].lower() in QUESTION_WORDS and node in tree.root.children:
                # We can consider the question word as one of the entities for the direct child of a root
                # e.g. [E1] Who [/E1] is the wife of [E2] Barack Obama [/E2] ?
                e2_begin = 0
                e2_end = len(tree.tokens[0])
            else:
                # We only have one entity, so we add a dummy token at the beginning of the sequence to consider as E2
                new_token = ' [{}] '.format(node.type.value)
                sequence = new_token + sequence
                offset = len(new_token)
                e1_begin, e1_end, e2_begin, e2_end = offset + e1_begin, offset + e1_end, 0, offset
        else: 
            e2_begin, e2_end = offset_for_node_union(tree, e2_nodes)

        node_vs_sequence[node.id] = {
            'text': sequence,
            'id': '{}${}'.format(tree.id, node.id),
            'subject': text[e1_begin:e1_end],
            'object':text[e2_begin:e2_end],
            'subject_begin': e1_begin,
            'subject_end': e1_end,
            'object_begin': e2_begin,
            'object_end': e2_end,
        }

        if len(node.kb_resources) > 0:
            node_vs_sequence[node.id]['relation'] = node.kb_resources[0] # TODO Consider others 

    return node_vs_sequence

def parse_trees_to_relation_extraction_format(parse_trees_file_path, output_file_path):
    with open(parse_trees_file_path, 'r', encoding='utf-8') as input_file:
        trees = json.load(input_file)
        trees = [question for question in trees if 'root' in question and question['root']]
        trees = list(map(lambda question: QueryTree.from_dict(question), trees))
        trees = list(filter(lambda x: SYNTAX_CHECKER.validate(x), trees))
    
    sequences = []
    for tree in trees:
        sequences.extend(generate_relation_extraction_sequences(tree).values())
        
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(sequences, output_file)


# class BertFormatTransform(object):
#     def __init__(self, max_sequence_length: int):
#         self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
#         self.max_sequence_length = max_sequence_length

#     def __call__(self, sample):
#         text = sample['text']
#         label = sample['label']

#         subject_text = sample['text'][sample['subject_begin']:sample['subject_end']]
#         object_text = sample['text'][sample['object_begin']:sample['object_end']]

#         tokens = ['[CLS]'] + self.tokenizer.tokenize(text) + ['[SEP]'] + self.tokenizer.tokenize(subject_text) + ['[SEP]'] + self.tokenizer.tokenize(object_text) + ['[SEP]']

#         token_ids = self.tokenizer.convert_tokens_to_ids(tokens)
#         token_ids = pad_sequences([token_ids], maxlen=self.max_sequence_length, dtype="long", value=0, truncating="post", padding="post")[0]
#         attention_mask = np.array([int(token_id > 0) for token_id in token_ids]).reshape(token_ids.shape)

#         return {'token_ids': torch.LongTensor(token_ids), 'attention_mask': torch.Tensor(attention_mask), 'label': label}


