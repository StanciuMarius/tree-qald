from common.query_tree import NodeType
from common.knowledge_base import ResourceType

QUERY_TEMPLATE_FILE_PATH                        = r'services\query_generator\static_files\query_template.sparql'
ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH             = r'services\query_generator\static_files\argfunc_subquery_template.sparql'
SUBQUERY_TEMPLATE_FILE_PATH                     = r'services\query_generator\static_files\subquery_template.sparql'
COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH    = r'services\query_generator\static_files\comparator_count_subquery_template.sparql'
COUNT_ENTITY_TEMPLATE_FILE_PATH                 = r'services\query_generator\static_files\count_entity_template.sparql'
EXISTS_TEMPLATE_FILE_PATH                       = r'services\query_generator\static_files\exists_template.sparql'
OCCUPATION_TEMPLATE_FILE_PATH                   = r'services\query_generator\static_files\occupation_template.sparql'
ENTITY_SETS = { NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.ARGMAXCOUNT, NodeType.ARGMINCOUNT, NodeType.SAMPLE, NodeType.GREATER, NodeType.LESS, NodeType.GREATERCOUNT, NodeType.LESSCOUNT, NodeType.TOPN, NodeType.PROPERTY, NodeType.ENTITY}
TYPE_RELATION = 'a'
RELATION_EXTRACTION_VARIABLE = '?relation'
TRIPLE_PATTERN = '\n{} {} {}.\n'
BIND_PATTERN   = '\nBIND(IF({} {} {}, {}, {}) AS {})\n'
VALUE_BINDING_PATTERN = '\nVALUES {} {{ {} }}'
ARGMAX_PATTERN = 'ORDER BY DESC({}) LIMIT {}\n'
ARGMIN_PATTERN = 'ORDER BY ASC({}) LIMIT 1\n'
ARGNTH_PATTERN = 'ORDER BY ASC({}) OFFSET {} LIMIT 1\n'
COUNT_VARIABLE_PATTERN = 'COUNT(DISTINCT {})'
DATATYPE_FILTER_ELEMENT   = 'datatype({VARIABLE}) = <{TYPE}>'
DATATYPE_FILTER_SEPARATOR = ' || '
DATATYPE_FILTER_WRAPPER = 'FILTER({CONSTRAINTS}).'


with open(OCCUPATION_TEMPLATE_FILE_PATH, 'r', encoding='utf-8') as file: OCCUPATION_FILTER_TEMPLATE = file.read()

OCCUPATION_SUPERCLASSES = set([
    'http://dbpedia.org/class/yago/Person106326797',
    'http://dbpedia.org/class/yago/Person100007846'
])

RELATION_MAPPING_BLACKLIST = set([
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    'http://dbpedia.org/ontology/wikiPageWikiLink',
    'http://dbpedia.org/ontology/wikiPageID',
    'http://www.w3.org/2002/07/owl#sameAs'
    ])