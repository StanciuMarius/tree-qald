import os
import sys
import time
import json
import traceback

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

@knowledge_base_service.route('/run_sparql_query', methods=['GET'])
@cross_origin()
def run_sparql_query():
    try:
        input_json_object = json.loads(request.args.get('input'))
        query_body = input_json_object['query_body']
        return_variable = input_json_object['return_variable']

        values: List[str] = KB_OPERATOR.run_query(query_body, return_variable)
        return jsonify(values)
    except:
        traceback.print_exc(file=sys.stdout)
        return 'Bad input', 400
    
def run_knowledge_base_service():
    knowledge_base_service.run(host='0.0.0.0', port=PORTS['KNOWLEDGE_BASE'])

if __name__ == '__main__':
    run_knowledge_base_service()

