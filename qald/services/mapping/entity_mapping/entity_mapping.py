
from tqdm import tqdm

import sys
import os
sys.path.insert(0, os.getcwd())
from services.mapping.constants import ENTITY_LEXICON_PATH

'''
    Class that finds knowledge base resources corresponding to small texts.

    It simply stores a lexicon of entities in a dictionary. The lexicon contains aggregated information
    from DBPedia disambiguates and country denonyms.

    E.g. "french" -> "dbpedia.org/resource/France"
    E.g. "Obama" -> "dbpedia.org/resource/Barack_Obama"

'''
class EntityMapping:
    def __init__(self, lexicon_path: str):
        
        self.text_vs_resources = {}

        with open(ENTITY_LEXICON_PATH, 'r', encoding='utf-8') as r:
            lines = r.readlines()[-100:]
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
    
    def spacy_similarity(a, b):
        if not a or not b:
            return 0.0
        a_doc = spacy_nlp(a)
        b_doc = spacy_nlp(b)
        try:

            return a_doc.similarity(b_doc)
        except:
            print('Error in getting spacy similarity for %s: %s' %(a, b))
            return 0.0

    def map_entity(self, entity_text: str):
        
        # Do some preprocessing
        no_spaces = entity_text.replace(" ", "")
        no_spaces_lower = no_spaces.lower()

        result = None

        if no_spaces in self.text_vs_resources:
            result = self.text_vs_resources[no_spaces]
        elif no_spaces_lower in self.text_vs_resources:
            result = self.text_vs_resources[no_spaces_lower]
        
        if result:
            result = 'http://dbpedia.org/resource/' + result + '>'
        
        return [result]


# entity_mapper = EntityMapping(ENTITY_LEXICON_PATH)
# print(entity_mapper.map_entity('hypnotiq'))
# print(entity_mapper.map_entity('hysterical'))