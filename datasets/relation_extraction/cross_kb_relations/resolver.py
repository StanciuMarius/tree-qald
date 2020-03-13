import sys
import os
sys.path.insert(0, os.getcwd())
import json
import common.knowledge_base as knowledge_base
from typing import List

EQUIVALENT_RELATIONS_DATASET_PATH = r'datasets\relation_extraction\cross_kb_relations\data\equivalent_relations.json'



class EquivalentRelationResolver(object):
    def __init__(self):
        self.kb_vs_generic_relations = {}
        self.generic_vs_kb_relations = {}
        with open(EQUIVALENT_RELATIONS_DATASET_PATH, 'r', encoding='utf-8') as file:
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
                equivalent_relations = [self.__reverse_relation(relation) for relation in equivalent_relations]
            return equivalent_relations
        else:
            reversed_relation_uri = self.__reverse_relation(relation_uri) 
            if relation_uri in self.kb_vs_generic_relations:
                return self.kb_vs_generic_relations[relation_uri]
            elif reversed_relation_uri in self.kb_vs_generic_relations:
                return self.kb_vs_generic_relations[reversed_relation_uri]

        return None
 
    def __reverse_relation(self, relation_uri: str):
        return relation_uri[1:] if '_' == relation_uri[0] else '_' + relation_uri


# r = EquivalentRelationResolver()
# print(r('http://freebase.com/location/location/contains'))