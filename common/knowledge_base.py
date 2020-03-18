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


LITERAL_DATATYPES = {
    ResourceType.DATE: ['http://www.w3.org/2001/XMLSchema#date', 'http://www.w3.org/2001/XMLSchema#gYear', 'http://www.w3.org/2001/XMLSchema#gMonth', 'http://www.w3.org/2001/XMLSchema#gYearMonth', 'http://www.w3.org/2001/XMLSchema#gMonthDay', 'http://www.w3.org/2001/XMLSchema#gDay'],
    ResourceType.NUMERAL: ['http://www.w3.org/2001/XMLSchema#integer', 'http://www.w3.org/2001/XMLSchema#decimal', 'http://www.w3.org/2001/XMLSchema#int', 'http://www.w3.org/2001/XMLSchema#double', 'http://www.w3.org/2001/XMLSchema#float', 'http://www.w3.org/2001/XMLSchema#short'],
    ResourceType.STRING:  ['http://www.w3.org/2001/XMLSchema#string']
}

COMPARABLE_DATATYPES = [*LITERAL_DATATYPES[ResourceType.DATE], *LITERAL_DATATYPES[ResourceType.NUMERAL], *LITERAL_DATATYPES[ResourceType.STRING]]