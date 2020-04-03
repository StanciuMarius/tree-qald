import os
import sys
sys.path.insert(0, os.getcwd())

import json
from typing import Tuple
import services.knowledge_base.constants as constants
from common.knowledge_base import KnowledgeBase, ResourceType
from common.query_tree import QueryTree

os.environ['JENA_HOME'] = constants.JENA_PATH

class KnowledgeBaseOperator(object):

    def __init__(self):
        self.cache = {}

    def run_query(self, query: str, return_variable: str):
        cache_key = query + "|" + return_variable
        if return_variable:
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        with open(constants.QUERY_FILE_PATH, 'w', encoding='ascii', newline='\n') as file:
            file.write(query)

        os.system(constants.JENA_COMMAND)
        with open(constants.RESULTS_FILE_PATH, 'r', encoding='utf-8') as data_file:
            try:
                content = json.load(data_file)
            except:
                raise Exception("Error parsing: {}")
        if return_variable:
            result = []
            for element in content['results']['bindings']:
                try:
                    value = element[return_variable]['value']
                    if value not in constants.RESULT_BLACKLIST:
                        result.append(value)
                except:
                    pass
        else:
            result = content['boolean']

        self.cache[cache_key] = result
        return result

# os.system(constants.JENA_COMMAND)
# with open(constants.RESULTS_FILE_PATH, 'r', encoding='utf-8') as data_file:
#     content = json.load(data_file)

# for element in content['results']['bindings']:
#     value = element['e']['value']
#     print(value)

