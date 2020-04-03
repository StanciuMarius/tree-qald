
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
        self.label_vs_entity = {}

        if not os.path.exists(constants.ENTITY_LEXICON_PATH):
            print("No entity lexicon was found. Generating it at {}".format(constants.ENTITY_LEXICON_PATH))
            self.__generate_lexicon()
        else:
            with open(constants.ENTITY_LEXICON_PATH, encoding="utf-8") as file:
                lines = file.readlines()
            
            for line in tqdm(lines, desc='Loading entity lexicon'):
                label, entities = line.split('\t')
                self.label_vs_entity[label] = entities.split(' ')
            print("Finished loading entity lexicon!")

        # with open(constants.ENTITY_LEXICON_PATH, 'r', encoding='utf-8') as r:
        #     lines = r.readlines()
        #     for line in tqdm(lines, desc='Loading entity lexicon'):
        #         tokens = line.rstrip('\t\n').split('\t')

        #         firstCandidate = tokens[1].split(' ')
        #         bestCandidate = firstCandidate[0]
        #         importance = int(firstCandidate[1])
        #         for tok in tokens[2:]:
        #             candidate = tok.lstrip(' ').split(' ')
        #             if int(candidate[1]) > importance:
        #                 importance = int(candidate[1])
        #                 bestCandidate = candidate[0]
                
        #         self.text_vs_resources[tokens[0].lower()] = bestCandidate
           

    def __generate_lexicon(self):
        def process_ttl(path):
            with open(path, 'r', encoding='utf-8') as file:
                for line in tqdm(file, desc='Processing {}'.format(path)):
                    try:
                        label, _, entity, _ = line.split(' ')
                        label = label.split('/')[-1].replace('>', '').replace('(disambiguation)', '').replace('_', ' ').strip().lower()
                        label_from_entity = entity.split('/')[-1].replace('>', '').replace('_', ' ').strip().lower()
                        entity = entity[29:-1] # get rid of '<http://dbpedia.org/resource/' and '>'
                        if label_from_entity in self.label_vs_entity:
                            self.label_vs_entity[label_from_entity].insert(0, entity) # The label generated from the entity itself has priority
                        else:
                            self.label_vs_entity[label_from_entity] = [entity]
                        if label in self.label_vs_entity:
                            self.label_vs_entity[label].append(entity)
                        else:
                            self.label_vs_entity[label] = [entity]
                    except:
                        print("Error parsing line: " + line)
                        continue

        process_ttl(constants.ENTITY_REDIRECTS_DATASET_PATH)
        process_ttl(constants.ENTITY_DISAMBIGUATIONS_DATASET_PATH)

        with open(constants.ENTITY_LEXICON_PATH, 'w', encoding='utf-8') as file:
            for label, entities in self.label_vs_entity.items():
                file.write(label + '\t' + ' '.join(entities) + '\n')
            

    def __call__(self, entity_text: str):
        # Preprocess the entity text in various ways, resulting in more versions to try to find in the lexicon
        entity_text = entity_text.lower()
        versions = [entity_text]

        # No stopwords
        tokens = word_tokenize(entity_text)
        no_stopwords_tokens = [word for word in tokens if not word in stopwords.words()]
        no_stopwords = ' '.join(no_stopwords_tokens)
        versions.append(no_stopwords)

        # Inversions
        no_stopwords_reversed = ' '.join(reversed(no_stopwords_tokens))
        versions.append(no_stopwords_reversed)

        # Extra word
        for index in range(len(tokens)):
            removed_word = ' '.join(tokens[:index] + tokens[index + 1:])
            if removed_word:
                versions.append(removed_word)


        result = []
        print("Trying to map: " + '|'.join(versions))
        for version in versions:
            if version in self.label_vs_entity:
                result = self.label_vs_entity[version]
                break
        
        result = [constants.DBPEDIA_RESOURCE_PREFIX + entity for entity in result][:1]
        print("Result: " + '|'.join(result))
    
        return result

    def __test__(self):
        assert self('Hotel California') == ['http://dbpedia.org/resource/Hotel_California']
        assert self('Ceres') == ['http://dbpedia.org/resource/Ceres']
        assert self('Obama') == ['http://dbpedia.org/resource/Barack_Obama']
