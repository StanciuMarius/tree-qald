import sys
import os
sys.path.insert(0, os.getcwd())

from random import shuffle
import json
import torch
from tqdm import tqdm 
from datasets.relation_extraction.relation_extraction_dataset import RelationExtractionDataset
import services.mapping.relation_mapping.relation_classifier.preprocessing as preprocessing
import services.mapping.relation_mapping.relation_classifier.constants as constants
from services.mapping.relation_mapping.relation_classifier.BERT_Relation_Extraction.main_pretraining import main as pretrain
from services.mapping.relation_mapping.relation_classifier.BERT_Relation_Extraction.main_task import main as task
from torchvision import transforms

RELATION_EXTRACTION_DATASETS = [
    ('fewrel', 'train'),
    ('fewrel', 'validation'),
    ('nyt10', 'train'),
    ('nyt10', 'test'),
    ('simplequestions', 'train'),
    ('simplequestions', 'test'),
    ('simplequestions', 'validation'),
    ('tacred', 'train'),
    ('tacred', 'test'),
    ('tacred', 'development'),
    ('tree-qald', 'trees')
]

def train():
    '''
    Using BERT-Relation-Extraction submodule to train a BERT model on an aggregated dataset
    '''
    relation_transform = preprocessing.EquivalentRelationTransform(save_statistics=True)
    dataset = RelationExtractionDataset(RELATION_EXTRACTION_DATASETS, transform=transforms.Compose([
                                                            preprocessing.NormalizeRelationUriTransofrm(),
                                                            relation_transform,
                                                            preprocessing.BertRelationExtractionFormatTransform()]))
            
    
    statistics = {}
    examples = list(filter(lambda x: preprocessing.validate(x, statistics=statistics), [example for example in tqdm(dataset)]))
    # top_unknown_relations = sorted(list(relation_transform.unknown_relations.items()), key=lambda x: x[1], reverse=True)[:10]
    # for relation, count in top_unknown_relations: print(relation, ' ', count)
    for statistic, count in statistics.items(): print(statistic, ' ', count)
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
