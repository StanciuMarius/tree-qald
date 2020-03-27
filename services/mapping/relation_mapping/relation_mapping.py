

import os
import sys
import json
sys.path.insert(0, os.getcwd())

import services.mapping.constants as constants
from typing import List

from services.mapping.relation_mapping.pattern_matcher.pattern_matcher import RelationPatternMatcher
from services.mapping.relation_mapping.relation_classifier.preprocessing import generate_relation_extraction_sequence
from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
from common.knowledge_base import KnowledgeBase
from services.mapping.relation_mapping.relation_classifier.relation_classifier import RelationClassifier
from datasets.relation_extraction.cross_kb_relations.resolver import EquivalentRelationResolver



class RelationRanker(object):
    '''
    Ranks candidate knowledge base relations for a node using an ensamble of models.
    '''
    def __init__(self, patty_weight=0.3, classifier_weight=0.7):
        self.patty_weight = patty_weight
        self.classifier_weight = classifier_weight
        self.patty = RelationPatternMatcher()
        self.classifier = RelationClassifier()
        self.resolver = EquivalentRelationResolver()

    def __call__(self, text: str, subject_begin: int, subject_end: int, object_begin: int, object_end: int, candidates: List[str], **kwargs) -> List[str]:
        patty_scores      = self.patty(text, subject_begin, subject_end, object_begin, object_end, **kwargs)
        classifier_scores = self.classifier(text, subject_begin, subject_end, object_begin, object_end, **kwargs)
        
        # The classifier candidates are generic, convert them to dbpedia
        classifier_dbpedia_scores = []
        for relation, score in classifier_scores:
            dbpedia_relations = self.resolver(relation, kb=KnowledgeBase.DBPEDIA)
            classifier_dbpedia_scores.extend([(dbpedia_relation, score) for dbpedia_relation in dbpedia_relations])

        patty_scores      = {candidate: score for candidate, score in patty_scores}
        classifier_scores = {candidate: score for candidate, score in classifier_dbpedia_scores}
        
        def score(relation: str) -> float:
            patty_score = patty_scores[relation] if relation in patty_scores else 0.0
            classifier_score = classifier_scores[relation] if relation in classifier_scores else 0.0
            return self.classifier_weight * classifier_score + self.patty_weight * patty_score / (self.classifier_weight + self.patty_weight)

        debug_list = ['({}, {})'.format(candidate, score(candidate)) for candidate in candidates]
        print('Ranked relations: ',  '\n'.join(debug_list))

        candidates = sorted(candidates, key=score, reverse=True)
        return candidates

    def __test__(self):
        text = "Who is the oldest actor that stars in a movie directed by Quentin Tarantino?"
        subject = "movie"
        object = "Quentin Tarantino"
        subject_begin = text.find(subject)
        subject_end = subject_begin + len(subject)

        object_begin = text.find(object)
        object_end = object_begin + len(object)
        candidates = [
        "http://dbpedia.org/ontology/director",
        "http://dbpedia.org/ontology/editor",
        "http://dbpedia.org/ontology/writer",
        "http://dbpedia.org/ontology/producer",
        "http://dbpedia.org/ontology/narrator",
        "http://dbpedia.org/ontology/basedOn",
        "http://dbpedia.org/ontology/story",
        "http://dbpedia.org/ontology/cinematography",
        "http://dbpedia.org/ontology/starring"
        ]
        sorted_candidates = self(text, subject_begin, subject_end, object_begin, object_end, candidates)
        assert sorted_candidates[0] == "http://dbpedia.org/ontology/director"

if __name__ == '__main__':
    ranker = RelationRanker()
    ranker.__test__()