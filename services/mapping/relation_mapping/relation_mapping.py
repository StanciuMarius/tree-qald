

from services.mapping.constants import PATTY_DBPEDIA_PARAPHRASES_FILE_PATH
from services.mapping.relation_mapping.pattern_matching import RelationPatternMatcher


class RelationMapper(object):
    def __init__(self, patty_weight=0.33, classifier_weight=0.33, similarity_weight=0.33):
        self.patty_weight = patty_weight
        self.classifier_weight = classifier_weight
        self.similarity_weight = similarity_weight
        self.patty = RelationPatternMatcher(PATTY_DBPEDIA_PARAPHRASES_FILE_PATH)
        self.