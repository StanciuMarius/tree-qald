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

    def __init__(self, kb: KnowledgeBase=KnowledgeBase.DBPEDIA):
        self.sparql_templates = {}
        for key, path in constants.RELATION_RETRIVAL_SPARQL_TEMPLATE_PATHS.items():
            with open(path, 'r', encoding='utf-8') as file:
                self.sparql_templates[key] = str(file.read())

    def run_query(self, query: str, return_variable: str):

        with open(constants.QUERY_FILE_PATH, 'w', encoding='ascii', newline='\n') as file:
            file.write(query)

        result = []
        os.system(constants.JENA_COMMAND)
        with open(constants.RESULTS_FILE_PATH, 'r', encoding='utf-8') as data_file:
            content = json.load(data_file)

        for element in content['results']['bindings']:
            value = element[return_variable]['value']
            if value not in constants.RESULT_BLACKLIST:
                result.append(value)

        return result

    def retrieve_relations(self, subject=Tuple[ResourceType, str], object_=Tuple[ResourceType, str]):
        template_key = ((subject[0] if subject else None), (object_[0] if object_ and object_[0] not in constants.LITERAL_FILTERS else None))
        filters = constants.LITERAL_FILTERS[object_[0]] if object_ and object_[0] in constants.LITERAL_FILTERS else ''

        if template_key not in self.sparql_templates:
            raise "Unsupported operation: " + str(template_key)
            
        if subject and object_:
            query = self.sparql_templates[template_key].format(ARG1='<'+subject[1]+'>', ARG2='<'+object_[1]+'>', FILTERS=filters)
        elif subject:
            query = self.sparql_templates[template_key].format(ARG1='<'+subject[1]+'>', FILTERS=filters)
        elif object_:
            query = self.sparql_templates(template_key).format(ARG1='<'+object_[1]+'>', FILTER=filters)
        
        relations = self.run_query(query, 'property')

        return relations

# kb = KnowledgeBaseOperator()

# test_1 = kb.retrieve_relation((ResourceType.ENTITY, "http://dbpedia.org/resource/Barack_Obama"), (ResourceType.ENTITY, "http://dbpedia.org/resource/Michelle_Obama")) == ['http://dbpedia.org/ontology/spouse']
# test_2 = 'http://dbpedia.org/ontology/birthDate' in kb.retrieve_relation((ResourceType.ENTITY, "http://dbpedia.org/resource/Barack_Obama"), (ResourceType.DATE, "")) 
# test_3 = 'http://dbpedia.org/ontology/residence' in kb.retrieve_relation((ResourceType.ENTITY, "http://dbpedia.org/resource/Barack_Obama"), (ResourceType.TYPE, "http://dbpedia.org/ontology/Building")) 
# print(test_3)
