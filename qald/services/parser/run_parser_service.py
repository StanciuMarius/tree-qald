import os
import sys
import time

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

sys.path.insert(0, os.getcwd())
from services.parser.parser import parse as internal_parse
from services.constants import PORTS
from services.tasks import run_task, Task

from common.query_tree import QueryTree, SerializationFormat
parser_service = Flask(__name__)
cors = CORS(parser_service)
parser_service.config['CORS_HEADERS'] = 'Content-Type'

@parser_service.route('/parse', methods=['GET'])
@cross_origin()
def parse():
    query_text = request.args.get('input')
    if query_text:
        tree: QueryTree = internal_parse(query_text)
        treeSerializable = tree.to_serializable(SerializationFormat.ADJECENCY)
        tokens = run_task(Task.TOKENIZE, query_text)

        response = {
            'tree': treeSerializable,
            'tokens': tokens
        }
        return jsonify(response)
    else:
        return 'No query given', 400


def run_parser_service():
    parser_service.run(host='0.0.0.0', port=PORTS['PARSER'])


if __name__ == '__main__':
    run_parser_service()