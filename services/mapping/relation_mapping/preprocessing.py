import json
import numpy as np
from transformers import BertTokenizer
from keras.preprocessing.sequence import pad_sequences
from services.mapping.relation_mapping.constants import EQUIVALENT_RELATIONS_DATASET_PATH, KNOWLEDGE_BASES
from sklearn.preprocessing import LabelEncoder
from typing import List
import torch

UNKNOWN_LABEL = 'UNKNOWN'
def generate_equivalent_relations(dataset_relations: List[str]):
    kb_vs_generic_relations = {}
    with open(EQUIVALENT_RELATIONS_DATASET_PATH, 'r', encoding='utf-8') as file:
        relation_sets = json.load(file)['dataset']
        for relation_set in  relation_sets:
            label = relation_set['label']
            for kb in KNOWLEDGE_BASES:
                if kb in  relation_set:
                    for relation in relation_set[kb]:
                        kb_vs_generic_relations[relation] = label
    dataset_relation_aliases = []
    for relation in dataset_relations:
        if relation in kb_vs_generic_relations:
            dataset_relation_aliases.append(kb_vs_generic_relations[relation])
        else:
            dataset_relation_aliases.append(UNKNOWN_LABEL)
    dataset_relation_aliases = list(set(dataset_relation_aliases))

    return kb_vs_generic_relations, dataset_relation_aliases

class LabelEncoderTransform(object):
    def __init__(self, labels: List[str]):
        self.label_encoder = LabelEncoder()            
        self.label_encoder.fit(labels)
    
    def __call__(self, sample):
        sample['label'] = self.label_encoder.transform([sample['label']])[0]
        return sample

class LabelAliasTransform(object):
    def __init__(self, label_aliases: dict):
        self.label_aliases = label_aliases
      
    def __call__(self, sample):
        relation = sample['relation']
        reversed_relation = '_' + relation

        if relation in self.label_aliases:
            sample['label'] = self.label_aliases[relation]
        # TODO: reconsider reversed relations
        elif reversed_relation in self.label_aliases:
            sample['label'] = self.label_aliases[reversed_relation]
        else:
            sample['label'] = UNKNOWN_LABEL

        return sample


class BertFormatTransform(object):
    def __init__(self, max_sequence_length: int):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        self.max_sequence_length = max_sequence_length

    def __call__(self, sample):
        text = sample['text']
        label = sample['label']

        subject_text = sample['text'][sample['subject_begin']:sample['subject_end']]
        object_text = sample['text'][sample['object_begin']:sample['object_end']]

        tokens = ['[CLS]'] + self.tokenizer.tokenize(text) + ['[SEP]'] + self.tokenizer.tokenize(subject_text) + ['[SEP]'] + self.tokenizer.tokenize(object_text) + ['[SEP]']

        token_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        token_ids = pad_sequences([token_ids], maxlen=self.max_sequence_length, dtype="long", value=0, truncating="post", padding="post")[0]
        attention_mask = np.array([int(token_id > 0) for token_id in token_ids]).reshape(token_ids.shape)

        return {'token_ids': torch.LongTensor(token_ids), 'attention_mask': torch.Tensor(attention_mask), 'label': label}