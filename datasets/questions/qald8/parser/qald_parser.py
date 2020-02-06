import json


with open('datasets\questions\qald8\data\qald8.json', 'r', encoding='utf-8') as file:
    content = json.load(file)
questions = content['questions']

output = open('datasets\questions\qald8\data\qald8_questions_with_relations.txt', 'w+', encoding='utf-8')

for question in questions:
    text = [question_text['string'] for question_text in question['question'] if question_text['language'] == 'en'][0]
    id = question['id']
    query = question['query']['sparql']
    query.replace('\\n', '\n')
    import re

    relations = [token for token in re.split(' |\n', query) if ('ontology' in token or 'property' in token or 'dbo:' in token or 'dbp:' in token) and token != 'dbo:' and token != 'dbr:' and token != 'http://dbpedia.org/property/' and token != 'http://dbpedia.org/ontology/']
    relations = ' '.join(relations)
    output.write(id + '|' + text + '|' + relations + '\n')

output.close()
    