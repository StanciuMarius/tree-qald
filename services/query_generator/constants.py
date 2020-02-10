QUERY_TEMPLATE_FILE_PATH                        = r'services\query_generator\static_files\query_template.sparql'
ARGFUNC_SUBQUERY_TEMPLATE_FILE_PATH             = r'services\query_generator\static_files\argfunc_subquery_template.sparql'
COUNT_SUBQUERY_TEMPLATE_FILE_PATH               = r'services\query_generator\static_files\count_subquery_template.sparql'
COMPARATOR_COUNT_SUBQUERY_TEMPLATE_FILE_PATH    = r'services\query_generator\static_files\comparator_count_subquery_template.sparql'
COUNT_ENTITY_TEMPLATE_FILE_PATH                 = r'services\query_generator\static_files\count_entity_template.sparql'
EXISTS_TEMPLATE_FILE_PATH                       = r'services\query_generator\static_files\exists_template.sparql'
ENTITY_SETS = {'ARGMAX', 'ARGMIN', 'ARGNTH', 'ARGMAXCOUNT', 'ARGMINCOUNT', 'SAMPLE', 'GREATER', 'LESS', 'GREATERCOUNT', 'LESSCOUNT', 'TOPN', 'PROPERTY', 'ENTITY'}
TYPE_RELATION = 'a'

TRIPLE_PATTERN = '\t{} {} {}.\n'
BIND_PATTERN   = '\tBIND(IF({} {} {}, {}, {}) AS {})\n'
ARGMAX_PATTERN = 'ORDER BY DESC({}) LIMIT {}.\n'
ARGMIN_PATTERN = 'ORDER BY ASC({}) LIMIT 1.\n'
ARGNTH_PATTERN = 'ORDER BY ASC({}) OFFSET {} LIMIT 1.\n'