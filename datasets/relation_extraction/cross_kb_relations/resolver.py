import json

EQUIVALENT_RELATIONS_DATASET_PATH = r'datasets\relation_extraction\cross_kb_relations\data\equivalent_relations.json'
KNOWLEDGE_BASES = ['dbpedia', 'tacred', 'wikidata', 'freebase']

class EquivalentRelationResolver(object):
    def __init__(self):
        self.kb_vs_generic_relations = {}
        with open(EQUIVALENT_RELATIONS_DATASET_PATH, 'r', encoding='utf-8') as file:
            relation_sets = json.load(file)['dataset']
            for relation_set in  relation_sets:
                label = relation_set['label']
                for kb in KNOWLEDGE_BASES:
                    if kb in  relation_set:
                        for relation in relation_set[kb]:
                            self.kb_vs_generic_relations[relation] = label

    
    def __call__(self, relation_uri: str):
        reversed_relation_uri = '_' + relation_uri

        if relation_uri in self.kb_vs_generic_relations:
            return self.kb_vs_generic_relations[relation_uri]
        elif reversed_relation_uri in self.kb_vs_generic_relations:
            return self.kb_vs_generic_relations[reversed_relation_uri]
        
        return None    
