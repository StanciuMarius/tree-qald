

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



class RelationMapper(object):
    '''
    An ensamble model based on a neural model and a pattern-matching model for relation extraction.

    It finds the knowledge-base relation correspondent to a text subject-object pair.
    Prior candidates can be given to reduce the search space. In case no candidates are given,
    all the relations are considered.
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
        
        def compute_score(relation: str) -> float:
            reverse_relation = '_' + relation if '_' not in relation else relation.replace('_', '')

            patty_score = patty_scores[relation] if relation in patty_scores else 0.0
            classifier_score = classifier_scores[relation] if relation in classifier_scores else 0.0
            if relation in classifier_scores:
                classifier_score = classifier_scores[relation]
            elif reverse_relation in classifier_scores:
                classifier_score = classifier_scores[reverse_relation]
            else: 
                classifier_score = 0.0

            # Harmonic mean of the two
            final_score = self.classifier_weight * classifier_score + self.patty_weight * patty_score / (self.classifier_weight + self.patty_weight)
            return final_score, classifier_score, patty_score # Last two are for debugging purposes

        if not candidates:
            # If no prior candidates are provided, we consider all kb relations
            candidates = list(set(list(classifier_scores.keys()) + list(patty_scores.keys()))) # All possible relations

        # We pick the highest ranked candidates (multiple candidates if they all have the same score)
        candidates = [(candidate, compute_score(candidate)) for candidate in candidates]
        candidates = sorted(candidates, key=lambda x: x[1][0], reverse=True)
        result = [candidate[0] for candidate in candidates if candidate[1][0] == candidates[0][1][0]]
        print('='*20)
        print("text: " + text)
        print("subject: " + text[subject_begin:subject_end])
        print("object: " + text[object_begin:object_end])
        print('Picked {}\n from \n{}\n'.format('\n'.join(result), '\n'.join(str(candidate) for candidate in candidates[:min(len(candidates), 20)])))
        print('='*20)

        return result

    def __test1__(self):
        text = "Give me all actors starring in movies directed by William Shatner."
        subject = "William Shatner"
        object = "movies"
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
            "http://dbpedia.org/ontology/starring",
        ]
        kb_relations = self(text, subject_begin, subject_end, object_begin, object_end, candidates)
        assert kb_relations[0] == "http://dbpedia.org/ontology/director"

    def __test2__(self):
        text = "Are Barack Obama and Michelle Obama married?"
        subject = "Barack Obama"
        object = "Michelle Obama"
        subject_begin = text.find(subject)
        subject_end = subject_begin + len(subject)

        object_begin = text.find(object)
        object_end = object_begin + len(object)
        candidates = [] # This is a typical EXISTS_RELATION case so we give no candidates
        kb_relations = self(text, subject_begin, subject_end, object_begin, object_end, candidates)
        assert "http://dbpedia.org/ontology/spouse" in kb_relations

if __name__ == '__main__':
    ranker = RelationMapper()
    ranker.__test1__()
    # ranker.__test2__()