import os
import sys
import time

from flask import Flask, request, jsonify

sys.path.insert(0, os.getcwd())
from services.nlp.nlp import tokenize as internal_tokenize
from services.constants import PORTS

nlp_service = Flask(__name__)

@nlp_service.route('/tokenize', methods=['GET'])
def tokenize():
    text = request.args.get('input')
    if text:
        tokens = internal_tokenize(text)
        return jsonify(tokens)
    else:
        return 'No query given', 400

def run_nlp_service():
    nlp_service.run(host='0.0.0.0', port=PORTS['NLP'])

if __name__ == '__main__':
    run_nlp_service()