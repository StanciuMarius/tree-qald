import os
import sys
import time
import json

from flask import Flask, request, jsonify

sys.path.insert(0, os.getcwd())
from services.mapping.mapping import map_relation as internal_map_relation
from services.constants import PORTS

mapping_service = Flask(__name__)

@mapping_service.route('/map_relation', methods=['GET'])
def map_relation():
    def is_valid(input: dict):
        return input and 'text' in  input and 'subject_begin' in input and 'subject_end' in input and 'object_begin' in input and 'object_end' in input
    
    input = json.loads(request.args.get('input'))
    
    if is_valid(input):
        text = input['text']
        subject_begin = input['subject_begin']
        subject_end = input['subject_end']
        object_begin = input['object_begin']
        object_end = input['object_end']
        
        candidates = internal_map_relation(text, subject_begin, subject_end, object_begin, object_end)
        
        return jsonify(candidates)
    else:
        return 'No query given', 400


def run_mapping_service():
    mapping_service.run(host='0.0.0.0', port=PORTS['MAPPING'])

if __name__ == '__main__':
    run_mapping_service()