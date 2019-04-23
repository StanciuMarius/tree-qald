import os
import sys
import time

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

sys.path.insert(0, os.getcwd())
from services.parser.parser import parse as internal_parse
from services.parser.parser import example as internal_example

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
        tokens = run_task(Task.TOKENIZE, query_text)
        tree: QueryTree = internal_parse(tokens)
        serializable_tree = tree.to_serializable(SerializationFormat.HIERARCHICAL_DICT)

        response = {
            'tree': serializable_tree,
            'tokens': tokens
        }
        return jsonify(response)
    else:
        return 'No query given', 400


@parser_service.route('/example', methods=['GET'])
@cross_origin()
def example():
    try:
        index = int(request.args.get('input'))
    except:
        return 'Input should be an integer representing the index of the example', 400
    
    tree, tokens = internal_example(index)
    serializable_tree = tree.to_serializable(SerializationFormat.HIERARCHICAL_DICT)

    response = {
        'tree': treeSerializable,
        'tokens': tokens
    }

    return jsonify(response)


def run_parser_service():
    parser_service.run(host='0.0.0.0', port=PORTS['PARSER'])


if __name__ == '__main__':
    run_parser_service()