import json


with open('datasets/qald8/qald8.json', 'r', encoding='utf-8') as file:
    content = json.load(file)
questions = content['questions']

output = open('datasets/qald8/qald8_questions.txt', 'w+', encoding='utf-8')

for question in questions:
    text = [question_text['string'] for question_text in question['question'] if question_text['language'] == 'en'][0]
    id = question['id']
    query = question['query']['sparql']
    query.replace('\\n', '\n')
    output.write(id + '|' + text + '\n')

output.close()
    