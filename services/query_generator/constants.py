QUERY_TEMPLATE_FILE_PATH = r'services\query_generator\static_files\query_template.sparql'
COUNT_ARG_SUBQUERY_TEMPLATE_FILE_PATH = r'services\query_generator\static_files\count_subquery_template.sparql'
COUNT_PROPERTY_TEMPLATE_FILE_PATH = r'services\query_generator\static_files\count_property.template.sparql'
ENTITY_SETS = {'ARGMAX', 'ARGMIN', 'ARGNTH', 'ARGMAXCOUNT', 'ARGMINCOUNT', 'SAMPLE', 'GREATER', 'LESS', 'GREATERCOUNT', 'LESSCOUNT', 'TOPN', 'PROPERTY', 'ENTITY'}
TYPE_RELATION = 'a'

TRIPLE_PATTERN = '\t{} {} {}.\n'
BIND_PATTERN   = '\tBIND(IF({} {} {}, {}, {}) AS {})\n'
ARGMAX_PATTERN = 'ORDER BY DESC({}) LIMIT 1.\n'
ARGMIN_PATTERN = 'ORDER BY ASC({}) LIMIT 1.\n'
ARGNTH_PATTERN = 'ORDER BY ASC({}) OFFSET {} LIMIT 1.\n'