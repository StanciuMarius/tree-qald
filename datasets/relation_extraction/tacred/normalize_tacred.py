import json
import os
from tqdm import tqdm

def normalize_tacred(source_path):
    file_name = os.path.basename(source_path)
    file_name = file_name.split('.')[0]
    output_path = os.path.join(r'datasets\relation_extraction\tacred\data', file_name + '_normalized.json')
    if os.path.exists(output_path): return output_path

    normalized_examples = []
    bad_examples = 0
    with open(source_path, 'r', encoding='utf-8') as input_file, open(output_path, 'w', encoding='utf-8') as file:
        examples = json.load(input_file)

        for example in tqdm(examples, desc='Normalizing {}'.format(source_path)):
            
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
                bad_examples += 1
                continue

            normalized_examples.append({
                'dataset': source_path,
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
        json.dump(normalized_examples, file, indent=4)
    
    print("{} had {} un-normalizable examples: ".format(source_path, bad_examples))

    return output_path
