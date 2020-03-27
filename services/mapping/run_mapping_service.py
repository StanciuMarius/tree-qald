import os
import sys
import traceback
import time
import json

from flask import Flask, request, jsonify
sys.path.insert(0, os.getcwd())
from services.constants import PORTS

from services.mapping.relation_mapping.relation_mapping import RelationPatternMatcher, RelationRanker
from services.mapping.entity_mapping.entity_mapping import EntityMapping
from services.mapping.type_mapping.type_mapping import TypeMapper
from services.mapping.constants import PATTY_DBPEDIA_PARAPHRASES_FILE_PATH, TYPES_TRIE_PATH

mapping_service = Flask(__name__)

RELATION_RANKER = RelationRanker()
ENTITY_MAPPER = EntityMapping()
TYPE_MAPPER = TypeMapper()

@mapping_service.route('/rank_relations', methods=['GET'])
def rank_relations():
    try:
        input = json.loads(request.args.get('input'))    
        candidates = RELATION_RANKER(**input)

        return jsonify(candidates)

    except:
        traceback.print_exc(file=sys.stdout)
        return 'Bad query', 400

@mapping_service.route('/map_entity', methods=['GET'])
def map_entity():

    input_obj = json.loads(request.args.get('input'))
    try:    
        text = input_obj['text']
        entity_begin = input_obj['entity_begin']
        entity_end = input_obj['entity_end']

        entity_text = text[entity_begin: entity_end]
        candidates = ENTITY_MAPPER(entity_text)
        return jsonify(candidates)
    except:
        traceback.print_exc(file=sys.stdout)
        return 'Bad query', 400

@mapping_service.route('/map_type', methods=['GET'])
def map_type():
    def is_valid(input: dict):
        return input and 'text' in input and 'type_begin' in input and 'type_end'
    
    input = json.loads(request.args.get('input'))
    
    if is_valid(input):
        text = input['text']
        type_begin = input['type_begin']
        type_end = input['type_end']
        
        type_text = text[type_begin: type_end]
        candidates = TYPE_MAPPER(type_text)

        return jsonify(candidates)
    else:
        return 'No query given', 400

def run_mapping_service():
    mapping_service.run(host='0.0.0.0', port=PORTS['MAPPING'])

if __name__ == '__main__':
    run_mapping_service()