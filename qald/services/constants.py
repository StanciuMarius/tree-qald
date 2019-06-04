PORTS = {
    'APP': 5000,
    'PARSER': 5001,
    'MAPPING': 5002,
    'NLP': 5003,
    'QUERY': 5004,
}

TASKS = {
    'tokenize' : 'NLP',
    'remove_punctuation' : 'NLP',
    'pos_tag': 'NLP',
    'spacy_process': 'NLP',
    'parse' : 'PARSER',
    'map_relation': 'MAPPING'
}

URL_ROOT = 'http://localhost'
