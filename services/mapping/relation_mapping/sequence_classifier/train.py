import sys
import os
sys.path.insert(0, os.getcwd())

from random import shuffle
import json
import torch
from tqdm import tqdm 
from datasets.relation_extraction.relation_extraction_dataset import RelationExtractionDataset
from services.mapping.relation_mapping.sequence_classifier.preprocessing import EquivalentRelationTransform, BertRelationExtractionFormatTransform, NormalizeRelationUriTransofrm, parse_trees_to_relation_extraction_format, UNKNOWN_LABEL, validate
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
    parse_trees_to_relation_extraction_format(PARSE_TREES_DATASET_PATH, constants.TEMP_PARSE_TREES_RELATION_EXTRACTION_DATASET_PATH)
    paths = list(RELATION_EXTRACTION_DATASET_PATHS)# + [TEMP_PARSE_TREES_RELATION_EXTRACTION_DATASET_PATH]

    dataset = RelationExtractionDataset(paths, transform=transforms.Compose([
                                                            NormalizeRelationUriTransofrm(),
                                                            EquivalentRelationTransform(),
                                                            BertRelationExtractionFormatTransform()]))
            
    
    train_size = int(constants.TRAIN_TEST_SPLIT_RATIO * len(dataset))
    validation_size = len(dataset) - train_size
    train_dataset, validation_dataset = torch.utils.data.random_split(dataset, [train_size, validation_size])

    examples = list(filter(validate, [example for example in tqdm(dataset)]))
    num_classes = len(set([example['relation'] for example in examples]))

    # We have to store the number of classes in a file because it's needed to load the model (for later inference)
    with open(constants.NUM_CLASSES_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(num_classes)

    # print("There are {} valid examples with {} distinct classes.".format(len(examples), num_classes))
    # train_size = int(TRAIN_TEST_SPLIT_RATIO * len(examples))
    # shuffle(examples)
    # train_examples, validation_examples = examples[:train_size], examples[train_size:]
    # with open(TEMP_TESTSET_FOR_SUBMODULE_PATH, 'w') as file:
    #     json.dump(validation_examples, file)

    # with open(TEMP_TRAINSET_FOR_SUBMODULE_PATH, 'w') as file:
    #     json.dump(train_examples, file)


    # print(eq_transform.unknown_relation_count, '/', len(dataset))
    train_args = ["--test_data", constants.TEMP_TESTSET_FOR_SUBMODULE_PATH,
                  "--train_data", constants.TEMP_TRAINSET_FOR_SUBMODULE_PATH,
                  "--additional_tokens_path", constants.ADDITIONAL_TOKENS_FILE_PATH,
                  "--temp_folder_path", constants.TEMP_FOLDER_FOR_SUBMODULE_PATH,
                  "--num_classes", str(num_classes),
                  "--num_epochs", str(constants.BERT_TRAIN_EPOCHS),
                  "--infer", str(1),
                  "--train", str(0)]
    # pretrain(['--pretrain_data', r'services\mapping\relation_mapping\temp\cnn.txt'])
    task(train_args)

train()

# from tqdm import tqdm
# import json
# import numpy as np
# import time
# import datetime
# import random
# import os
# import sys
# import cProfile
# import torch


# from services.mapping.relation_mapping.constants import BERT_MAX_SEQUENCE_LENGTH, BERT_TRAIN_EPOCHS, BERT_LR, BERT_EPS, TRAIN_TEST_SPLIT_RATIO, BERT_BATCH_SIZE
# from transformers import BertForSequenceClassification, AdamW
# from transformers import get_linear_schedule_with_warmup
# from common.logging import format_time, flat_accuracy
# from common.gpu import get_device
# from datasets.relation_extraction.relation_extraction_dataset import RelationExtractionDataset
# from services.mapping.relation_mapping.preprocessing import LabelAliasTransform, BertFormatTransform, LabelEncoderTransform, generate_equivalent_relations
# from torchvision import transforms, datasets
# from torch.utils.data import DataLoader, TensorDataset

# def main():
#     # Read dataset
#     dataset = RelationExtractionDataset()
#     label_vs_alias, used_labels = generate_equivalent_relations(dataset.labels) # Use the Equivalent relations dataset to unify relations
#     dataset.transform = transforms.Compose([
#         LabelAliasTransform(label_vs_alias),
#         LabelEncoderTransform(used_labels), 
#         BertFormatTransform(BERT_MAX_SEQUENCE_LENGTH)])

#     # Split into train/test
#     train_size = int(TRAIN_TEST_SPLIT_RATIO * len(dataset))
#     validation_size = len(dataset) - train_size
#     train_dataset, validation_dataset = torch.utils.data.random_split(dataset, [train_size, validation_size])

#     # Open pretrained bert sentence classifier
#     model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(used_labels))
#     model.cuda()
#     num_steps = train_size * BERT_TRAIN_EPOCHS
#     optimizer = AdamW(model.parameters(), lr=BERT_LR, eps=BERT_EPS)
#     scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=num_steps)
#     seed_val = 42
#     random.seed(seed_val)
#     np.random.seed(seed_val)
#     torch.manual_seed(seed_val)
#     torch.cuda.manual_seed_all(seed_val)
#     device = get_device()

#     # Store the average loss after each epoch so we can plot them.
#     loss_values = []

#     train_dataloader = DataLoader(train_dataset, batch_size=BERT_BATCH_SIZE, shuffle=True)
#     validation_dataloader  = DataLoader(validation_dataset,  batch_size=BERT_BATCH_SIZE, shuffle=True)

#     # For each epoch...
#     for epoch_i in range(0, BERT_TRAIN_EPOCHS):

#         print("")
#         print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, BERT_TRAIN_EPOCHS))
#         print('Training...')
#         t0 = time.time()
#         total_loss = 0
#         model.train()

#         for step, batch in enumerate(train_dataloader):

#             if step % 40 == 0 and not step == 0:
#                 # Log progress
#                 elapsed = format_time(time.time() - t0)
#                 print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

#             b_token_ids = batch['token_ids'].to(device)
#             b_attention_masks = batch['attention_mask'].to(device)
#             b_labels = batch['label'].to(device)

#             model.zero_grad()        

#             # Forward pass
#             outputs = model(b_token_ids, token_type_ids=None, attention_mask=b_attention_masks, labels=b_labels)
#             loss = outputs[0]
#             total_loss += loss.item()

#             # Backward pass
#             loss.backward()
#             torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

#             optimizer.step()
#             scheduler.step()

#         avg_train_loss = total_loss / len(train_dataloader)            
#         loss_values.append(avg_train_loss)

#         print("")
#         print("  Average training loss: {0:.2f}".format(avg_train_loss))
#         print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))
#         print("")

#         print("Running Validation...")
#         t0 = time.time()
#         model.eval()

#         eval_loss, eval_accuracy = 0, 0
#         nb_eval_steps, nb_eval_examples = 0, 0

#         for batch in validation_dataloader:
            
#             # batch = tuple(t.to(device) for t in batch)
#             b_token_ids = batch['token_ids'].to(device)
#             b_attention_masks = batch['attention_mask'].to(device)
#             b_labels = batch['label'].to(device)

#             with torch.no_grad():        
#                 # Forward pass
#                 outputs = model(b_token_ids, token_type_ids=None, attention_mask=b_attention_masks)
            
#             logits = outputs[0]
#             logits = logits.detach().cpu().numpy()
#             label_ids = b_labels.to('cpu').numpy()

#             tmp_eval_accuracy = flat_accuracy(logits, label_ids)
#             eval_accuracy += tmp_eval_accuracy

#             nb_eval_steps += 1

#         print("  Accuracy: {0:.2f}".format(eval_accuracy/nb_eval_steps))
#         print("  Validation took: {:}".format(format_time(time.time() - t0)))

#     print("")
#     print("Training complete!")

# main()
# # cProfile.run('main()')
