
import os
import sys
import json
import requests

from enum import Enum

sys.path.insert(0, os.getcwd())
from services.constants import URL_ROOT, PORTS, TASKS

class Task(Enum):
    TOKENIZE = 'tokenize'
    POS_TAGS = 'pos_tag'
    SPACY_PROCESS = 'spacy_process'
    REMOVE_PUNCTUATION = 'remove_punctuation'
    PARSE = 'parse'
    MAP_RELATIONS = 'map_relations'
    MAP_ENTITY = 'map_entity'
    MAP_TYPE = 'map_type'
    RETRIEVE_RELATIONS = 'retrieve_relations'
    RUN_SPARQL_QUERY = 'run_sparql_query'
    GENERATE_QUERY = 'generate_query'


def run_task(task: Task, input):
    json_input = input if type(input) == str  else json.dumps(input)
    service = TASKS[task.value]
    URL = URL_ROOT + ':' + str(PORTS[service]) + '/' + task.value 
    request = requests.Request('GET', URL, params = {'input': json_input}).prepare()
    try:
        session = requests.Session()
        response = session.send(request)
    except requests.exceptions.RequestException as e:
        print('Could not establish connection to the {} service. Try starting it with \'python services/{}/run_{}_service.py\''.format(service, service.lower(), service.lower()))
        sys.exit(1)
    if response.status_code == 200:
        output_text = response.text
        output = json.loads(output_text)
        return output
    else:
        return None


# Example of running a task from Task enum
# print(run_task(Task.TOKENIZE, "hello world"))
# print(run_task(Task.PARSE, "hello world"))
# print(run_task(Task.MAP_ENTITY, {
#     'text': 'U.S. president Lincoln ',
#     'entity_begin': 0,
#     'entity_end': len('U.S. president Lincoln')
# }))

# test_1 = kb.retrieve_relation(, (ResourceType.ENTITY, "http://dbpedia.org/resource/Michelle_Obama")) == ['http://dbpedia.org/ontology/spouse']
