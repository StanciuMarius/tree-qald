import os
import sys
import time
import json

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

sys.path.insert(0, os.getcwd())
from services.knowledge_base.knowledge_base import KnowledgeBaseOperator
from services.constants import PORTS
from services.tasks import run_task, Task
from common.knowledge_base import ResourceType

KB_OPERATOR = KnowledgeBaseOperator()

knowledge_base_service = Flask(__name__)
cors = CORS(knowledge_base_service)
knowledge_base_service.config['CORS_HEADERS'] = 'Content-Type'

@knowledge_base_service.route('/retrieve_relations', methods=['GET'])
@cross_origin()
def retrieve_relations():
    # try:
    input_json_object = json.loads(request.args.get('input'))
    subject = input_json_object['subject']
    object_ = input_json_object['object']
    if subject:
        subject[0] = ResourceType[subject[0]]
    if object_:
        object_[0] = ResourceType[object_[0]]

    relations: List[str] = KB_OPERATOR.retrieve_relations(subject, object_)
    return jsonify(relations)
    # except:
    #     return 'Bad input', 400

def run_knowledge_base_service():
    knowledge_base_service.run(host='0.0.0.0', port=PORTS['KNOWLEDGE_BASE'])

if __name__ == '__main__':
    run_knowledge_base_service()

