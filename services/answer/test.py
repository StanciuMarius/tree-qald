import json
import os
import sys
from tqdm import tqdm
from typing import List

sys.path.insert(0, os.getcwd())

from services.answer.answer import answer as internal_answer
with open('datasets\questions\qald8\data\qald8.json', 'r', encoding='utf-8') as file:
    content = json.load(file)
questions = content['questions']

f1_sum = 0
tree_log = []
questions = questions
for question in tqdm(questions):
    text = [question_text['string'] for question_text in question['question'] if question_text['language'] == 'en'][0]
    try:
        golden_answer = [list(binding.values())[0]['value'] for binding in question['answers'][0]['results']['bindings']]
    except:
        golden_answer = question['answers'][0]['boolean']

    predicted_answer, query, tree = internal_answer(text)

    if isinstance(golden_answer, bool):
        if  isinstance(predicted_answer, bool) and golden_answer == predicted_answer:
            precision, recall, f1 = 1.0, 1.0, 1.0
        else:
            precision, recall, f1 = 0.0, 0.0, 0.0
    elif predicted_answer == None or isinstance(predicted_answer, bool):
        precision, recall, f1 = 0.0, 0.0, 0.0
    else:
        TP, FP, FN = 0, 0, 0
        golden_answer_set = set(golden_answer)

        for uri in predicted_answer:
            if uri in golden_answer_set:
                TP += 1.0
            else:
                FP += 1.0
        
        FN = len(golden_answer) - TP
        
        precision = TP / (TP + FP + 0.00001)
        recall    = TP / (TP + FN + 0.00001)
        if recall + precision < 0.00001:
            f1 = 0.0
        else:
            f1 = 2 * (recall * precision) / (recall + precision + 0.00001)

    f1_sum += f1
    tree_log.append({
        'tree': tree,
        'query': query,
        'text': text,
        'predicted_answer': predicted_answer,
        'golden_answer': golden_answer,
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

macro_f1 = f1_sum / len(questions)
print('Macro f1: {}'.format(macro_f1))

with open(r'services\answer\test_log.json', 'w', encoding='utf-8') as file:
    json.dump(tree_log, file)






