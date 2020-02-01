GRAMMAR_FILE_PATH               = r'services\parser\static_files\grammar'
MODEL_FILE_PATH                 = r'services\parser\tmp\model\crf-bilstm'
NCRFPP_REPOSITORY_PATH          = r'services\parser\tree2labels\NCRFpp'


# Train dataset
TRAIN_TEST_RATIO = 0.9
QUESTION_SET_FILE_PATH          = r'datasets\parsing\data\constituency_annotated_questions.json'
MODEL_CONFIG_FILE_PATH          = r'services\parser\tmp\model\crf-bilstm.config'

# Temporary files
INTERMEDIATE_QUERY_FILE_PATH    = r'services\parser\tmp\intermediate_input_query.seq_lu'
INTERMEDIATE_OUTPUT_FILE_PATH   = r'services\parser\tmp\intermediate_output.paran'
INTERMEDIATE_TEST_FILE_PATH     = r'services\parser\tmp\intermediate_test.paran'
INTERMEDIATE_TRAIN_FILE_PATH    = r'services\parser\tmp\intermediate_train.paran'
FINAL_OUTPUT_FILE_PATH          = r'services\parser\tmp\final_output.param'
DATASET_NAME                    = r'DUMMY' # If you change this, do it in the config file (MODEL_CONFIG_FILE) as well
