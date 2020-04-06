import json
from typing import List

import sys
import os
sys.path.insert(0, os.getcwd())

import common.knowledge_base as knowledge_base
from datasets.datasets import DatasetResolver

class EquivalentRelationResolver(object):
    def __init__(self):
        self.dataset_resolver = DatasetResolver()
        self.kb_vs_generic_relations = {}
        self.generic_vs_kb_relations = {}
        with open(self.dataset_resolver('equivalent-relations', 'relations'), 'r', encoding='utf-8') as file:
            relation_sets = json.load(file)['dataset']
            for relation_set in  relation_sets:
                label = relation_set['label']
                for kb in knowledge_base.KnowledgeBase:
                    if label not in self.generic_vs_kb_relations:
                        self.generic_vs_kb_relations[label] = {}
                    self.generic_vs_kb_relations[label][kb.value] = []
                    if kb.value in relation_set:
                        for relation in relation_set[kb.value]:
                            self.kb_vs_generic_relations[relation] = label
                            self.generic_vs_kb_relations[label][kb.value].append(relation)
    

    
    def __call__(self, relation_uri: str, kb: knowledge_base.KnowledgeBase=None) -> List[str]:
        '''
        Returns equivalent relations to the @param relation_uri.
        If a kb is not specified, the generic label of the relation's equivalence set is returned.
        If a kb is specified, all the equivalent relations from that kb are returned.
        '''
        is_reversed = '_' == relation_uri[0]
        if kb:
            equivalent_relations = []
            if relation_uri in self.generic_vs_kb_relations and kb.value in self.generic_vs_kb_relations[relation_uri]:
                equivalent_relations = list(self.generic_vs_kb_relations[relation_uri][kb.value])

            if is_reversed:
                equivalent_relations = [self.reverse_relation(relation) for relation in equivalent_relations]
            return equivalent_relations
        else:
            reversed_relation_uri = self.reverse_relation(relation_uri) 
            if relation_uri in self.kb_vs_generic_relations:
                return self.kb_vs_generic_relations[relation_uri]
            elif reversed_relation_uri in self.kb_vs_generic_relations:
                return self.reverse_relation(self.kb_vs_generic_relations[reversed_relation_uri])

        return None
 
    def reverse_relation(self, relation_uri: str):
        return relation_uri[1:] if '_' == relation_uri[0] else '_' + relation_uri

    def __test__(self):
        relation = self('http://freebase.com/location/location/contains')
        assert relation == '_location'

        relation = self('tacred:per:country_of_birth')
        assert relation == 'originPlace'

        relation = self('http://wikidata.org/entity/P1340')
        assert relation == 'color'

        relation = self('_http://dbpedia.org/ontology/birthDate')
        assert relation == '_birthDate'

        relation = self.reverse_relation("_http://dbpedia.org/ontology/birthPlace")
        assert relation == 'http://dbpedia.org/ontology/birthPlace'

        relation = self.reverse_relation("http://dbpedia.org/ontology/birthPlace")
        assert relation == '_http://dbpedia.org/ontology/birthPlace'

if __name__ == '__main__':
    resolver = EquivalentRelationResolver()
    resolver.__test__()