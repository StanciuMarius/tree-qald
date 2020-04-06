import json
import sys
import os
sys.path.insert(0, os.getcwd())

from datasets.datasets import DatasetResolver


valid = True
duplicates = []
invalid_keys = []
dataset_resolver = DatasetResolver()

with open(dataset_resolver('equivalent-relations', 'relations'), 'r', encoding='utf-8') as file:
    dataset = json.load(file)
    dataset['dataset'] = sorted(dataset['dataset'], key=lambda x: x['label'])
    labels = set()

    relation_vs_label = {}
    for relation_set in dataset['dataset']:
        label = relation_set['label']
        for kb in {'dbpedia', 'freebase', 'tacred', 'wikidata'}:
            if kb in relation_set:
                for relation in relation_set[kb]:
                    if relation in relation_vs_label:
                        duplicates.append(relation)
                    else:
                        relation_vs_label[relation] = label
        
        for key in relation_set.keys():
            if key not in {'label', 'description', 'dbpedia', 'freebase', 'tacred', 'wikidata'}:
                invalid_keys.append(key)
if duplicates:
    print('The following relations appear in multiple entity sets: ', ' '.join(duplicates))
    valid = False

if invalid_keys:
    print('Invalid keys found:', ' '.join(invalid_keys))
    valid = False

if valid:
    print('Dataset appears valid!')