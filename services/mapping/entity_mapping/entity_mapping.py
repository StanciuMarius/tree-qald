
from tqdm import tqdm

import sys
import os
sys.path.insert(0, os.getcwd())
import services.mapping.constants as constants
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

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
                
                self.text_vs_resources[tokens[0].lower()] = bestCandidate
           
        print("Finished loading entity lexicon!")

    def __call__(self, entity_text: str):
        # Preprocess the entity text in various ways, resulting in more versions to try to find in the lexicon
        entity_text = entity_text.lower()
        versions = [entity_text]

        # No stopwords
        tokens = word_tokenize(entity_text)
        no_stopwords_tokens = [word for word in tokens if not word in stopwords.words()]
        no_stopwords = ''.join(no_stopwords_tokens)
        versions.append(no_stopwords)

        # Inversions
        no_stopwords_reversed = ''.join(reversed(no_stopwords_tokens))
        versions.append(no_stopwords_reversed)

        # Extra word
        for index in range(len(tokens)):
            removed_word = ''.join(tokens[:index] + tokens[index + 1:])
            versions.append(removed_word)


        result = []
        print("Trying to map: " + '|'.join(versions))
        for version in versions:
            if version in self.text_vs_resources:
                result.append(self.text_vs_resources[version])
                break
        
        result = [constants.DBPEDIA_RESOURCE_PREFIX + entity for entity in result]
        print("Result: " + ' '.join(result))
    
        return result

# entity_mapper = EntityMapping(ENTITY_LEXICON_PATH)
# print(entity_mapper.map_entity('hypnotiq'))
# print(entity_mapper.map_entity('hysterical'))