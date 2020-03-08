from enum import Enum

class KnowledgeBase(Enum):
    DBPEDIA  = 'dbpedia'
    TACRED   = 'tacred'
    WIKIDATA = 'wikidata'
    FREEBASE = 'freebase'