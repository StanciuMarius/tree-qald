PORTS = {
    'APP': 5000,
    'PARSER': 5001,
    'MAPPING': 5002,
    'NLP': 5003,
    'QUERY_GENERATOR': 5004,
    'ANSWER': 5005,
    'KNOWLEDGE_BASE': 5006
}

TASKS = {
    'tokenize' : 'NLP',
    'remove_punctuation' : 'NLP',
    'pos_tag': 'NLP',
    'spacy_process': 'NLP',
    'parse' : 'PARSER',
    'rank_relations': 'MAPPING',
    'map_entity': 'MAPPING',
    'map_type': 'MAPPING',
    'retrieve_relations': 'KNOWLEDGE_BASE',
    'run_sparql_query': 'KNOWLEDGE_BASE',
    'generate_query': 'QUERY_GENERATOR'
}

URL_ROOT = 'http://localhost'
