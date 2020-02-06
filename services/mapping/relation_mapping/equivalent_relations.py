from services.tasks import run_task, Task
import os
import sys
from typing import List
import json

sys.path.insert(0, os.getcwd())


datasets = [
    r'datasets\relation_extraction\fewrel\train_normalized.json',                          #0.48
    r'datasets\relation_extraction\fewrel\val_normalized.json',                            #0.43
    r'datasets\relation_extraction\NYT10\test_normalized.json',                            #0.96
    r'datasets\relation_extraction\NYT10\train_normalized.json',                           #0.7
    r'datasets\relation_extraction\tacred\data\dev_normalized.json',                       #0.9
    r'datasets\relation_extraction\tacred\data\test_normalized.json',                      #0.9
    r'datasets\relation_extraction\tacred\data\train_normalized.json',                     #0.9
    r'datasets\relation_extraction\simple_questions\data\simple_normalized_test_val.json', #0.35
    r'datasets\relation_extraction\simple_questions\data\simple_normalized_train.json',    #0.35
]

class EquivalentRelationResolver:
    def __init__(self, dataset_path):
        with open(dataset_path, 'r', encoding='utf-8') as dataset_file:
            self.relations = json.load(dataset_file)['dataset']
        
        self.uri_vs_relations = {}

        for relation in self.relations:
            if 'freebase' in relation:
                for uri in relation['freebase']:
                    self.uri_vs_relations[uri] = relation
            if 'tacred' in relation:
                for uri in relation['tacred']:
                    self.uri_vs_relations[uri] = relation
            if 'wikidata' in relation:
                for uri in relation['wikidata']:
                    self.uri_vs_relations[uri] = relation
            if 'dbpedia' in relation:
                for uri in relation['dbpedia']:
                    self.uri_vs_relations[uri] = relation
    def get_equivalent_relations(self, uri):
        if uri in self.uri_vs_relations:
            return self.uri_vs_relations[uri]
        if '_' + uri in self.uri_vs_relations:
            return self.uri_vs_relations['_' + uri]
        
        return []


relation_resolver = EquivalentRelationResolver(r'datasets\relation_extraction\properties\equivalent_properties.json')
examples = []
for dataset_path in datasets:

    with open(dataset_path, 'r', encoding='utf-8') as file:
        try:
            dataset = json.load(file)
        except:
            print('yo')

    examples.extend(dataset)

count = 0

freq = {}
for example in examples:
    equivalent_relation = relation_resolver.get_equivalent_relations(example['relation'])

    if equivalent_relation:
        if equivalent_relation['label'] not in freq:
            freq[equivalent_relation['label']] = 0
        freq[equivalent_relation['label']] += 1


print(sorted([(key, value) for key, value in freq.items()], key=lambda x: x[1]))
    


# examples = [
#     {
#         "subject_begin": 0,
#         "subject_end": 3,
#         "object_begin": 19,
#         "object_end": 31,
#         "text": "Who is the wife of Barack Obama?"
#     },
# ]

# print(examples[0]['text'][0:3], examples[0]['text'][19:31])
# for example in examples:
#     candidates = run_task(Task.MAP_RELATION, json.dumps(example))
#     print(candidates)