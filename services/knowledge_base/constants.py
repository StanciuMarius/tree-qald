import os
import platform
import sys
sys.path.insert(0, os.getcwd())

from enum import Enum
from common.knowledge_base import ResourceType

JENA_PATH = os.path.abspath(r'services/knowledge_base/apache-jena-3.14.0')
if platform.system() == 'Windows':
    JENA_EXECUTABLE = os.path.join(JENA_PATH, r'bat/rsparql').lower()
else:
    JENA_EXECUTABLE = os.path.join(JENA_PATH, r'bin/rsparql').lower()

VIRTUOSO_HOST      = r'http://dbpedia.org/sparql'
QUERY_FILE_PATH    = os.path.abspath('services/knowledge_base/temp/query.sparql').lower() # JENA is really pretentious about uppercase letters in paths
RESULTS_FILE_PATH  = os.path.abspath('services/knowledge_base/temp/results.json').lower() 
JENA_COMMAND = "{} --service {} --query {} --results=json > {}".format(JENA_EXECUTABLE, VIRTUOSO_HOST, QUERY_FILE_PATH, RESULTS_FILE_PATH).replace('\\', '/')

RELATION_RETRIVAL_SPARQL_TEMPLATE_PATHS = {
    (ResourceType.TYPE,    ResourceType.TYPE):       r'services\knowledge_base\static\TYPE_TYPE.template.sparql',
    (ResourceType.TYPE,    None):                    r'services\knowledge_base\static\TYPE_NONE.template.sparql',
    (None,    ResourceType.TYPE):                    r'services\knowledge_base\static\NONE_TYPE.template.sparql',
    (ResourceType.ENTITY,    ResourceType.TYPE):     r'services\knowledge_base\static\ENTITY_TYPE.template.sparql',
    (ResourceType.TYPE,    ResourceType.ENTITY):     r'services\knowledge_base\static\TYPE_ENTITY.template.sparql',
    (ResourceType.ENTITY,    None):                  r'services\knowledge_base\static\ENTITY_NONE.template.sparql',
    (None,    ResourceType.ENTITY):                  r'services\knowledge_base\static\NONE_ENTITY.template.sparql',
    (ResourceType.ENTITY,    ResourceType.ENTITY):   r'services\knowledge_base\static\ENTITY_ENTITY.template.sparql',
}

LITERAL_FILTERS = {
    ResourceType.DATE: 'FILTER(datatype(?object) = xsd:date || datatype(?object) = xsd:gYear || datatype(?object) = xsd:gMonth || datatype(?object) = xsd:gYearMonth || datatype(?object) = xsd:gMonthDay || datatype(?object) = xsd:gDay).',
    ResourceType.NUMERAL: 'FILTER(datatype(?object) = xsd:integer || datatype(?object) = xsd:decimal || datatype(?object) = xsd:int || datatype(?object) = xsd:double || datatype(?object) = xsd:float || datatype(?object) = xsd:short).',
    ResourceType.STRING: 'FILTER(datatype(?object) = xsd:string).'
}

RESULT_BLACKLIST = {
    'http://dbpedia.org/ontology/wikiPageWikiLink',
}