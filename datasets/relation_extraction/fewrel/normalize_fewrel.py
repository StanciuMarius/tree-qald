import json

train = r'datasets\relation_extraction\fewrel\train.json'
val = r'datasets\relation_extraction\fewrel\val.json'
output_train = r'datasets\relation_extraction\fewrel\train_normalized.json'
output_val = r'datasets\relation_extraction\fewrel\val_normalized.json'


def normalize_fewrel(source_path, destination_path, dataset_name):
    normalized_examples = []
    with open(source_path, 'r', encoding='utf-8') as input_file, open(destination_path, 'w', encoding='utf-8') as output_file:
        input_json = json.load(input_file)
        for relation, examples in input_json.items():

            for id, example in enumerate(examples):
                text = ' '.join(example['tokens'])
                tokens = example['tokens']
                
                head_text = ' '.join([tokens[token] for token in example['h'][2][0]])
                head_id = example['h'][1]
                head_begin = text.find(head_text)
                head_end = head_begin + len(head_text)

                tail_text = ' '.join([tokens[token] for token in example['t'][2][0]])
                tail_id = example['t'][1]
                tail_begin = text.find(tail_text)
                tail_end = tail_begin + len(tail_text)
                
                if head_begin == -1 or tail_begin == -1:
                    print("bad question")
                    continue

                normalized_examples.append({
                    'dataset': dataset_name,
                    'id': relation + str(id),
                    'subject_begin': head_begin,
                    'subject_end': head_end,
                    'subject_id': 'https://www.wikidata.org/entity/' + head_id,
                    'object_begin': tail_begin,
                    'object_end': tail_end,
                    'object_id': 'https://www.wikidata.org/entity/' + tail_id,
                    'relation': 'http://www.wikidata.org/entity/' + relation,
                    'text': text
                })
        json.dump(normalized_examples, output_file, indent=4)

        
# normalize_fewrel(val, output_val, 'fewrel_val')
normalize_fewrel(train, output_train, 'fewrel_train')
