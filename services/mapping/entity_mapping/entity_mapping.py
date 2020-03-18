
from tqdm import tqdm

import sys
import os
sys.path.insert(0, os.getcwd())
import services.mapping.constants as constants

'''
    Class that finds knowledge base resources corresponding to small texts.

    It simply stores a lexicon of entities in a dictionary. The lexicon contains aggregated information
    from DBPedia disambiguates and country denonyms.

    E.g. "french" -> "dbpedia.org/resource/France"
    E.g. "Obama" -> "dbpedia.org/resource/Barack_Obama"

'''
class EntityMapping:
    def __init__(self):
        
        self.text_vs_resources = {}

        with open(constants.ENTITY_LEXICON_PATH, 'r', encoding='utf-8') as r:
            lines = r.readlines()
            for line in tqdm(lines, desc='Loading entity lexicon'):
                tokens = line.rstrip('\t\n').split('\t')

                firstCandidate = tokens[1].split(' ')
                bestCandidate = firstCandidate[0]
                importance = int(firstCandidate[1])
                for tok in tokens[2:]:
                    candidate = tok.lstrip(' ').split(' ')
                    if int(candidate[1]) > importance:
                        importance = int(candidate[1])
                        bestCandidate = candidate[0]
                
                self.text_vs_resources[tokens[0]] = bestCandidate
           
        print("Finished loading entity lexicon!")

    def __call__(self, entity_text: str):
        # Do some preprocessing
        no_spaces = entity_text.replace(" ", "")
        no_spaces_lower = no_spaces.lower()

        result = []

        if no_spaces in self.text_vs_resources:
            result.append(self.text_vs_resources[no_spaces])
        elif no_spaces_lower in self.text_vs_resources:
            result.append(self.text_vs_resources[no_spaces_lower])
        
        result = [constants.DBPEDIA_RESOURCE_PREFIX + entity for entity in result]
    
        return result

# entity_mapper = EntityMapping(ENTITY_LEXICON_PATH)
# print(entity_mapper.map_entity('hypnotiq'))
# print(entity_mapper.map_entity('hysterical'))