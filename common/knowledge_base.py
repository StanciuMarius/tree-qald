from enum import Enum

class KnowledgeBase(Enum):
    DBPEDIA  = 'dbpedia'
    TACRED   = 'tacred'
    WIKIDATA = 'wikidata'
    FREEBASE = 'freebase'

class ResourceType(Enum):
    ENTITY      = 'ENTITY'
    TYPE        = 'TYPE'
    RELATION    = 'RELATION'
    DATE        = 'DATE'
    NUMERAL     = 'NUMERAL'
    STRING      = 'STRING'