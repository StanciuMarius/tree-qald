import json

train = r'datasets\relation_extraction\tacred\data\train.json'
test = r'datasets\relation_extraction\tacred\data\test.json'
dev = r'datasets\relation_extraction\tacred\data\dev.json'
output_train = r'datasets\relation_extraction\tacred\data\train_normalized.json'
output_test = r'datasets\relation_extraction\tacred\data\test_normalized.json'
output_dev = r'datasets\relation_extraction\tacred\data\dev_normalized.json'

def normalize_tacred(source_path, destination_path, dataset_name):

    normalized_examples = []
    bad_examples = 0
    with open(source_path, 'r', encoding='utf-8') as input_file, open(destination_path, 'w', encoding='utf-8') as destination_file:
        examples = json.load(input_file)

        for example in examples:
            
            tokens = example['token']
            text = ' '.join(tokens)
            relation = example['relation']

            head_text = ' '.join([tokens[token] for token in range(example['subj_start'], example['subj_end'] + 1)])
            head_begin = text.find(head_text)
            head_end = head_begin + len(head_text)

            tail_text = ' '.join([tokens[token] for token in range(example['obj_start'], example['obj_end'] + 1)])
            tail_begin = text.find(tail_text)
            tail_end = tail_begin + len(tail_text)

            if head_begin == -1 or tail_begin == -1:
                print("bad question: ", bad_examples)
                bad_examples += 1
                continue

            normalized_examples.append({
                'dataset': dataset_name,
                'id': example['id'],
                'subject_begin': head_begin,
                'subject_end': head_end,
                'subject_id': 'NA',
                'object_begin': tail_begin,
                'object_end': tail_end,
                'object_id': 'NA',
                'relation':  'tacred:' + relation,
                'text': text
            })
        json.dump(normalized_examples, destination_file, indent=4)

# normalize_tacred(dev, output_dev, 'tacred_dev')
# normalize_tacred(test, output_test, 'tacred_test')
normalize_tacred(train, output_train, 'tacred_train')
