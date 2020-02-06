import os
import sys
import time
import json

from flask import Flask, request

sys.path.insert(0, os.getcwd())
from services.nlp.nlp import \
                tokenize as internal_tokenize,\
                remove_punctuation as internal_remove_punctuation,\
                pos_tag as internal_pos_tag,\
                spacy_process as internal_spacy_process 
from services.constants import PORTS

nlp_service = Flask(__name__)

@nlp_service.route('/tokenize', methods=['GET'])
def tokenize():
    text = request.args.get('input')
    if text:
        tokens = internal_tokenize(text)
        return json.dumps(tokens)
    else:
        return 'No query given', 400


@nlp_service.route('/spacy_process', methods=['GET'])
def spacy_process():
    text = request.args.get('input')
    if text:
        spacy_dict = internal_spacy_process(text)
        return json.dumps(spacy_dict)
    else:
        return 'No query given', 400

@nlp_service.route('/pos_tag', methods=['GET'])
def pos_tag():
    text = request.args.get('input')
    if text:
        tags = internal_pos_tag(text)
        return json.dumps(tags)
    else:
        return 'No query given', 400


@nlp_service.route('/remove_punctuation', methods=['GET'])
def remove_punctuation():
    text = request.args.get('input')
    if text:
        processed_string = internal_remove_punctuation(text)
        return json.dumps(processed_string)
    else:
        return 'No query given', 400



def run_nlp_service():
    nlp_service.run(host='0.0.0.0', port=PORTS['NLP'])

if __name__ == '__main__':
    run_nlp_service()