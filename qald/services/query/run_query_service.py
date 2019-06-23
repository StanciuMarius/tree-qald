import os
import sys
import time

from flask import Flask, request, jsonify

sys.path.insert(0, os.getcwd())
from services.query.query import answer as internal_answer
from services.constants import PORTS

query_service = Flask(__name__)

@query_app.route('/query', methods=['GET'])
def parse():
    query_text = request.args.get('input')
    if query_text:
        answer = internal_answer(query_text)
        return jsonify(answer)
    else:
        return 'No query given', 400


def run_query_service():
    query_service.run(host='0.0.0.0', port=PORTS['QUERY'])


if __name__ == '__main__':
    run_query_service()