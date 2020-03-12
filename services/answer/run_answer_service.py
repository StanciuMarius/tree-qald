import os
import sys
import time

from flask import Flask, request, jsonify

sys.path.insert(0, os.getcwd())
from services.answer.answer import answer as internal_answer
from services.constants import PORTS

answer_service = Flask(__name__)

@answer_service.route('/answer', methods=['GET'])
def answer():
    query_text = request.args.get('input')
    if query_text:
        answer = internal_answer(query_text)
        return jsonify(answer)
    else:
        return 'No query given', 400


def run_query_service():
    answer_service.run(host='0.0.0.0', port=PORTS['ANSWER'])


if __name__ == '__main__':
    run_answer_service()