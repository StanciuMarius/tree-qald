import sys
import os
sys.path.insert(0, os.getcwd())

from random import shuffle
import json
import torch
from tqdm import tqdm 
from datasets.relation_extraction.relation_extraction_dataset import RelationExtractionDataset
import services.mapping.relation_mapping.sequence_classifier.preprocessing as preprocessing
import services.mapping.relation_mapping.sequence_classifier.constants as constants
# from services.mapping.relation_mapping.sequence_classifier.constants import #TEMP_PARSE_TREES_RELATION_EXTRACTION_DATASET_PATH, TEMP_TESTSET_FOR_SUBMODULE_PATH, TEMP_TRAINSET_FOR_SUBMODULE_PATH, TRAIN_TEST_SPLIT_RATIO, ADDITIONAL_TOKENS_FILE_PATH, TEMP_FOLDER_FOR_SUBMODULE_PATH, BERT_TRAIN_EPOCHS, NUM_CLASSES
from services.mapping.relation_mapping.sequence_classifier.BERT_Relation_Extraction.main_pretraining import main as pretrain
from services.mapping.relation_mapping.sequence_classifier.BERT_Relation_Extraction.main_task import main as task
from torchvision import transforms


RELATION_EXTRACTION_DATASET_PATHS = [
    r'datasets\relation_extraction\fewrel\data\train_normalized.json',
    r'datasets\relation_extraction\NYT10\data\train_normalized.json',
    r'datasets\relation_extraction\simple_questions\data\simple_normalized_train.json',
    r'datasets\relation_extraction\tacred\data\train_normalized.json',
]

PARSE_TREES_DATASET_PATH = r'datasets\parsing\data\constituency_annotated_questions.json'

def train():
    '''
    Using BERT-Relation-Extraction submodule to train a BERT model on an aggregated dataset
    '''
    preprocessing.parse_trees_to_relation_extraction_format(PARSE_TREES_DATASET_PATH, constants.TEMP_PARSE_TREES_RELATION_EXTRACTION_DATASET_PATH)
    paths = RELATION_EXTRACTION_DATASET_PATHS + [constants.TEMP_PARSE_TREES_RELATION_EXTRACTION_DATASET_PATH]

    dataset = RelationExtractionDataset(paths, transform=transforms.Compose([
                                                            preprocessing.NormalizeRelationUriTransofrm(),
                                                            preprocessing.EquivalentRelationTransform(),
                                                            preprocessing.BertRelationExtractionFormatTransform()]))
            
    
    # train_size = int(constants.TRAIN_TEST_SPLIT_RATIO * len(dataset))
    # validation_size = len(dataset) - train_size
    # train_dataset, validation_dataset = torch.utils.data.random_split(dataset, [train_size, validation_size])

    examples = list(filter(preprocessing.validate, [example for example in tqdm(dataset)]))
    shuffle(examples)

    num_classes = len(set([example['relation'] for example in examples]))
    print("There are {}/{} valid examples with {} distinct classes.".format(len(examples), len(dataset), num_classes))
    # We have to store the number of classes in a file because it's needed to load the model for later inference
    with open(constants.NUM_CLASSES_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(str(num_classes))

    train_size = int(constants.TRAIN_TEST_SPLIT_RATIO * len(examples))
    train_examples, validation_examples = examples[:train_size], examples[train_size:]

    with open(constants.TEMP_TESTSET_FOR_SUBMODULE_PATH, 'w') as file:
        json.dump(validation_examples, file)

    with open(constants.TEMP_TRAINSET_FOR_SUBMODULE_PATH, 'w') as file:
        json.dump(train_examples, file)

    # print(eq_transform.unknown_relation_count, '/', len(dataset))
    train_args = ["--test_data", constants.TEMP_TESTSET_FOR_SUBMODULE_PATH,
                  "--train_data", constants.TEMP_TRAINSET_FOR_SUBMODULE_PATH,
                  "--additional_tokens_path", constants.ADDITIONAL_TOKENS_FILE_PATH,
                  "--temp_folder_path", constants.TEMP_FOLDER_FOR_SUBMODULE_PATH,
                  "--num_classes", str(num_classes),
                  "--num_epochs", str(constants.BERT_TRAIN_EPOCHS),
                  "--batch_size", str(constants.BERT_BATCH_SIZE),
                  "--infer", str(0),
                  "--train", str(1)]
    # pretrain(['--pretrain_data', r'services\mapping\relation_mapping\temp\cnn.txt'])
    task(train_args)

train()
