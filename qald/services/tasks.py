
import os
import sys
import json
import requests
from enum import Enum

sys.path.insert(0, os.getcwd())
from services.constants import URL_ROOT, PORTS, TASKS

class Task(Enum):
    TOKENIZE = 'tokenize'
    PARSE = 'parse'

def run_task(task: Task, input):
    json_input = input if type(input) == str  else json.dumps(input)
    URL = URL_ROOT + ':' + str(PORTS[TASKS[task.value]]) + '/' + task.value + '?input=' + json_input
    try:
        response = requests.get(URL)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    output_text = response.text
    output = json.loads(response.text)

    return output


# Example of running a task from Task enum
# print(run_task(Task.TOKENIZE, "hello world"))
# print(run_task(Task.PARSE, "hello world"))