import json

FILE_PATHS = [
    # r'datasets\questions\freebaseqa\data\FreebaseQA-dev.json',
    r'datasets\questions\freebaseqa\data\FreebaseQA-train.json',
    # r'datasets\questions\freebaseqa\data\FreebaseQA-partial.json'
    # r'datasets\questions\freebaseqa\data\FreebaseQA-eval.json'
]
OUTPUT_FILE = r'datasets\questions\freebaseqa\data\questions_with_relations.txt'

question_texts = []
with open(OUTPUT_FILE, 'w') as output_file:
    for path in FILE_PATHS:
        with open(path, 'r', encoding='utf-8') as file:
            questions = json.load(file)['Questions']


        for question in questions:
            question_texts.append(question['RawQuestion'])
            relations = question['Parses'][0]['InferentialChain'].split('..')
            
            if len(relations) > 1:
                output_file.write(question['Question-ID'] + '|' + question['RawQuestion'] + '|' + ' '.join(relations) + '\n')    
