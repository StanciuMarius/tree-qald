
EQUIVALENT_RELATIONS_DATASET_PATH = r'datasets\relation_extraction\cross_kb_relations\data\equivalent_properties.json'
TEMP_TRAINSET_FOR_SUBMODULE_PATH = r'services\mapping\relation_mapping\temp\re_train.json'
TEMP_TESTSET_FOR_SUBMODULE_PATH = r'services\mapping\relation_mapping\temp\re_test.json'
ADDITIONAL_TOKENS_FILE_PATH = r'services\mapping\relation_mapping\temp\additional_tokens.csv'

KNOWLEDGE_BASES = ['dbpedia', 'tacred', 'wikidata', 'freebase']
TRAIN_TEST_SPLIT_RATIO = 0.8
BERT_MAX_SEQUENCE_LENGTH = 128
BERT_TRAIN_EPOCHS = 4
BERT_LR = 2e-5
BERT_EPS = 1e-8
BERT_BATCH_SIZE = 4
