import os
import sys
sys.path.insert(0, os.getcwd())

from services.mapping.relation_mapping.relation_classifier.BERT_Relation_Extraction.main_task import load_inferrer_from_trained
import services.mapping.relation_mapping.relation_classifier.constants as constants
import services.mapping.relation_mapping.relation_classifier.preprocessing as preprocessing 
import common.knowledge_base as knowledge_base

class RelationClassifier(object):
    def __init__(self):
        with open(constants.NUM_CLASSES_FILE_PATH, 'r', encoding='utf-8') as file:
            num_classes = str(file.read())
        self.inferrer = load_inferrer_from_trained(['--temp_folder_path', constants.TEMP_FOLDER_FOR_SUBMODULE_PATH, '--num_classes', num_classes])
        self.preprocessor = preprocessing.BertRelationExtractionFormatTransform()

    def __call__(self, text, subject_begin, subject_end, object_begin, object_end, **kwargs):
        sample = {
            'subject_begin': subject_begin,
            'subject_end': subject_end,
            'object_begin': object_begin,
            'object_end': object_end,
            'text': text
        }
        sequence = self.preprocessor(sample)['text']
        probabilities = self.inferrer.infer_one_sentence(sequence, return_probabilities=True)

        reverse_sample = {
            'subject_begin': object_begin,
            'subject_end': object_end,
            'object_begin': subject_begin,
            'object_end': subject_end,
            'text': text
        }
        reverse_sequence = self.preprocessor(sample)['text']
        reverse_probabilities = self.inferrer.infer_one_sentence(reverse_sequence, return_probabilities=True)

        final_probabilities = [(relation, (score + reverse_score) / 2) for (relation, score), (_, reverse_score) in zip(probabilities, reverse_probabilities)]
        return final_probabilities
        
