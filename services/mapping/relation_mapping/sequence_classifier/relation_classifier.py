import os
import sys
sys.path.insert(0, os.getcwd())

from services.mapping.relation_mapping.sequence_classifier.BERT_Relation_Extraction.main_task import load_inferrer_from_trained
import services.mapping.relation_mapping.sequence_classifier.constants as constants
from services.mapping.relation_mapping.sequence_classifier.preprocessing import BertRelationExtractionFormatTransform

class RelationClassifier(object):
    def __init__(self):
        with open(constants.NUM_CLASSES_FILE_PATH, 'r', encoding='utf-8') as file:
            num_classes = str(file.read())
        self.inferrer = load_inferrer_from_trained(['--temp_folder_path', constants.TEMP_FOLDER_FOR_SUBMODULE_PATH, '--num_classes', num_classes])
        self.preprocessor = BertRelationExtractionFormatTransform()

    def __call__(self, text, subject_begin, subject_end, object_begin, object_end):
        sample = {
            'subject_begin': subject_begin,
            'subject_end': subject_end,
            'object_begin': object_begin,
            'object_end': object_end,
            'text': text
        }
        sequence = self.preprocessor(sample)['text']
        probabilities = self.inferrer.infer_one_sentence(sequence, return_probabilities=True)
        return probabilities
        
model = RelationClassifier()
text         = "Who is the wife of Barack Obama?"
subject_text = "Barack Obama"
object_text  = "Who"
subject_index = text.find(subject_text)
object_index = text.find(object_text)

prediction = model(text, subject_index, subject_index + len(subject_text), object_index, object_index + len(object_text))
for x in prediction:
    print(x)
