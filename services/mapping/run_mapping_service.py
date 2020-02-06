import os
import sys
import time
import json

from flask import Flask, request, jsonify
sys.path.insert(0, os.getcwd())
from services.constants import PORTS

from services.mapping.relation_mapping.relation_mapping import RelationPatternMatcher
from services.mapping.entity_mapping.entity_mapping import EntityMapping
from services.mapping.type_mapping.type_mapping import TypeMapping
from services.mapping.constants import PATTY_DBPEDIA_PARAPHRASES_FILE_PATH, ENTITY_LEXICON_PATH, TYPES_TRIE_PATH

mapping_service = Flask(__name__)

RELATION_PATTERN_MATCHER = RelationPatternMatcher(PATTY_DBPEDIA_PARAPHRASES_FILE_PATH)
ENTITY_MAPPER = EntityMapping(ENTITY_LEXICON_PATH)
TYPE_MAPPER = TypeMapping()

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
        
        candidates = RELATION_PATTERN_MATCHER.find_relation(text, subject_begin, subject_end, object_begin, object_end)
        
        return jsonify(candidates)
    else:
        return 'No query given', 400

@mapping_service.route('/map_entity', methods=['GET'])
def map_entity():
    def is_valid(input: dict):
        return input and 'text' in input and 'entity_begin' in input and 'entity_end'
    
    input = json.loads(request.args.get('input'))
    
    if is_valid(input):
        text = input['text']
        entity_begin = input['entity_begin']
        entity_end = input['entity_end']

        entity_text = text[entity_begin: entity_end]
        candidates = ENTITY_MAPPER.map_entity(entity_text)
        
        return jsonify(candidates)
    else:
        return 'No query given', 400

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
        candidates = TYPE_MAPPER.get_best_types(type_text)

        return jsonify(candidates)
    else:
        return 'No query given', 400

def run_mapping_service():
    mapping_service.run(host='0.0.0.0', port=PORTS['MAPPING'])

if __name__ == '__main__':
    run_mapping_service()