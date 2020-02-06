import json

train = r'datasets\relation_extraction\NYT10\train.txt'
test = r'datasets\relation_extraction\NYT10\test.txt'
output_train = r'datasets\relation_extraction\NYT10\train_normalized.json'
output_test = r'datasets\relation_extraction\NYT10\test_normalized.json'


def normalize_nyt10(source_path, destination_path, dataset_name):

    normalized_examples = []
    bad_examples = 0
    with open(source_path, 'r', encoding='utf-8') as input_file, open(destination_path, 'w', encoding='utf-8') as destination_file:
        lines = input_file.readlines()

        for id, line in enumerate(lines):
            example = line.split('\t')
            
            text = example[5]

            relation = example[4]
            relation = relation if relation == 'NA' else 'http://rdf.freebase.com/ns' + relation

            head_text = example[2]
            head_id = example[0]
            head_begin = text.find(head_text)
            head_end = head_begin + len(head_text)

            tail_text = example[3]
            tail_id = example[1]
            tail_begin = text.find(tail_text)
            tail_end = tail_begin + len(tail_text)
            if head_begin == -1 or tail_begin == -1:
                print("bad question: ", bad_examples)
                bad_examples += 1
                continue

            normalized_examples.append({
                'dataset': dataset_name,
                'id': str(id),
                'subject_begin': head_begin,
                'subject_end': head_end,
                'subject_id': 'http://rdf.freebase.com/ns/' + head_id,
                'object_begin': tail_begin,
                'object_end': tail_end,
                'object_id': 'http://rdf.freebase.com/ns/' + tail_id,
                'relation':  relation,
                'text': text.replace('_', ' ')
            })
        json.dump(normalized_examples, destination_file, indent=4)

normalize_nyt10(test, output_test, 'nyt10_test')
#normalize_nyt10(train, output_train, 'nyt10_train')