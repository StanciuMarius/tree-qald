import json
import os
from tqdm import tqdm

def normalize_nyt10(source_path):
    file_name = os.path.basename(source_path)
    file_name = file_name.split('.')[0]
    output_path = os.path.join(r'datasets\relation_extraction\nyt10\data', file_name + '_normalized.json')
    if os.path.exists(output_path): return output_path

    normalized_examples = []
    bad_examples = 0
    with open(source_path, 'r', encoding='utf-8') as input_file, open(output_path, 'w', encoding='utf-8') as file:
        lines = input_file.readlines()

        for id, line in tqdm(enumerate(lines), desc='Normalizing {}'.format(source_path)):
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
                bad_examples += 1
                continue

            normalized_examples.append({
                'dataset': source_path,
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
        json.dump(normalized_examples, file, indent=4)

    print("{} had {} un-normalizable examples: ".format(source_path, bad_examples))
    return output_path