import json


valid = True
duplicates = []
invalid_keys = []
with open(r'datasets\relation_extraction\cross_kb_relations\data\equivalent_relations.json', 'r', encoding='utf-8') as file:
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