from common.query_tree import NodeType
from common.knowledge_base import ResourceType

QUERY_TEMPLATE_FILE_PATH                        = r'services\query_generator\static_files\query_template.sparql'
ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH             = r'services\query_generator\static_files\argfunc_subquery_template.sparql'
COUNT_SUBQUERY_TEMPLATE_FILE_PATH               = r'services\query_generator\static_files\count_subquery_template.sparql'
COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH    = r'services\query_generator\static_files\comparator_count_subquery_template.sparql'
COUNT_ENTITY_TEMPLATE_FILE_PATH                 = r'services\query_generator\static_files\count_entity_template.sparql'
EXISTS_TEMPLATE_FILE_PATH                       = r'services\query_generator\static_files\exists_template.sparql'
ENTITY_SETS = { NodeType.ARGMAX, NodeType.ARGMIN, NodeType.ARGNTH, NodeType.ARGMAXCOUNT, NodeType.ARGMINCOUNT, NodeType.SAMPLE, NodeType.GREATER, NodeType.LESS, NodeType.GREATERCOUNT, NodeType.LESSCOUNT, NodeType.TOPN, NodeType.PROPERTY, NodeType.ENTITY}
TYPE_RELATION = 'a'
RELATION_EXTRACTION_VARIABLE = '?relation'
TRIPLE_PATTERN = '\t{} {} {}.\n'
BIND_PATTERN   = '\tBIND(IF({} {} {}, {}, {}) AS {})\n'
VALUE_BINDING_PATTERN = 'VALUES {} {{ {} }}'
ARGMAX_PATTERN = 'ORDER BY DESC({}) LIMIT {}\n'
ARGMIN_PATTERN = 'ORDER BY ASC({}) LIMIT 1\n'
ARGNTH_PATTERN = 'ORDER BY ASC({}) OFFSET {} LIMIT 1\n'
DATATYPE_FILTER_ELEMENT   = 'datatype({VARIABLE}) = <{TYPE}>'
DATATYPE_FILTER_SEPARATOR = ' || '
DATATYPE_FILTER_WRAPPER = 'FILTER({CONSTRAINTS}).'


RELATION_MAPPING_BLACKLIST = set([
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    'http://dbpedia.org/ontology/wikiPageWikiLink'
    ])