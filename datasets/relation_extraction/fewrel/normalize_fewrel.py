import json
import os
from tqdm import tqdm

def normalize_fewrel(source_path):
    file_name = os.path.basename(source_path)
    file_name = file_name.split('.')[0]
    output_path = os.path.join(r'datasets\relation_extraction\fewrel\data', file_name + '_normalized.json')
    if os.path.exists(output_path): return output_path
    
    bad_examples = 0
    normalized_examples = []
    with open(source_path, 'r', encoding='utf-8') as input_file, open(output_path, 'w', encoding='utf-8') as output_file:
        input_json = json.load(input_file)
        for relation, examples in tqdm(input_json.items(), desc='Normalizing {}'.format(source_path)):

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
                    bad_examples += 1
                    continue

                normalized_examples.append({
                    'dataset': source_path,
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
    print("{} had {} un-normalizable examples: ".format(source_path, bad_examples))
    return output_path