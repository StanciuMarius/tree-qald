
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
    MAP_RELATION = 'map_relation'
    MAP_ENTITY = 'map_entity'
    MAP_TYPE = 'map_type'


def run_task(task: Task, input):
    json_input = input if type(input) == str  else json.dumps(input)
    service = TASKS[task.value]
    URL = URL_ROOT + ':' + str(PORTS[service]) + '/' + task.value + '?input=' + json_input
    try:
        response = requests.get(URL)
    except requests.exceptions.RequestException as e:
        print('Could not establish connection to the {} service. Try starting it with \'python services/{}/run_{}_service.py\''.format(service, service.lower(), service.lower()))
        sys.exit(1)

    output_text = response.text
    output = json.loads(output_text)

    return output

# Example of running a task from Task enum
# print(run_task(Task.TOKENIZE, "hello world"))
# print(run_task(Task.PARSE, "hello world"))