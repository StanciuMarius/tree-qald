import os
import sys
import traceback
import time
import json

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

sys.path.insert(0, os.getcwd())
from services.query_generator.query_generator import generate_query as internal_generate_query

from services.constants import PORTS
from services.tasks import run_task, Task

from common.query_tree import QueryTree, SerializationFormat
query_generator_service = Flask(__name__)
cors = CORS(query_generator_service)
query_generator_service.config['CORS_HEADERS'] = 'Content-Type'

@query_generator_service.route('/generate_query', methods=['GET'])
@cross_origin()
def generate_query():
    try:
        query_tree_dict = json.loads(request.args.get('input'))
        query, answer_variable = internal_generate_query(query_tree_dict)
        response = {
            "query_body": query,
            "return_variable": answer_variable
        }
        return jsonify(response)
    except:
        traceback.print_exc(file=sys.stdout)
        return 'Bad query', 400

def run_query_generator_service():
    query_generator_service.run(host='0.0.0.0', port=PORTS['QUERY_GENERATOR'])


if __name__ == '__main__':
    run_query_generator_service()