

import os
import sys
import json
sys.path.insert(0, os.getcwd())

import services.mapping.constants as constants
from services.mapping.relation_mapping.pattern_matcher.pattern_matcher import RelationPatternMatcher
from services.mapping.relation_mapping.relation_classifier.preprocessing import generate_relation_extraction_sequence
from common.query_tree import QueryTree, NodeType, RELATION_NODE_TYPES
# from services.mapping.relation_mapping.relation_classifier.relation_classifier import RelationClassifier



class RelationRanker(object):
    '''
    Ranks candidate knowledge base relations for a node using an ensamble of models.
    '''
    def __init__(self, patty_weight=0.3, classifier_weight=0.7):
        self.patty_weight = patty_weight
        self.classifier_weight = classifier_weight
        # self.patty = RelationPatternMatcher()
        # self.classifier = RelationClassifier()

    def __call__(self, text, subject_begin, subject_end, object_begin, object_end, candidates, **kwargs):
        # patty_candidates = self.patty(**sequence)

        candidates = sorted(candidates) # TODO Implement the sorting key
        return candidates