import json

FILE_PATHS = [
    # r'datasets\questions\comqa\data\comqa_train.json',
    r'datasets\questions\comqa\data\comqa_test.json',
    # r'datasets\questions\comqa\data\comqa_dev.json'
]
OUTPUT_FILE = r'datasets\questions\comqa\data\questions.txt'



question_texts = []
with open(OUTPUT_FILE, 'w') as output_file:

    for path in FILE_PATHS:
        with open(path, 'r', encoding='utf-8') as file:
            content = json.load(file)


        for example in content:
            if 'st ' in example['question']:
                output_file.write('comqa-test'+str(example['id']) + '|' + example['question'] + '\n')    


