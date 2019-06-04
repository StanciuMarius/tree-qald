from services.tasks import run_task, Task
import json

examples = [
    {
        "subject_begin": 0,
        "subject_end": 3,
        "object_begin": 19,
        "object_end": 31,
        "text": "Who is the wife of Barack Obama?"
    },
]

# print(examples[0]['text'][0:3], examples[0]['text'][19:31])
for example in examples:
    candidates = run_task(Task.MAP_RELATION, json.dumps(example))
    print(candidates)