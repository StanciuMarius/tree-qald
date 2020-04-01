import re
import json
import codecs
from tqdm import tqdm
from boltons.setutils import IndexedSet
import nltk

import sys
import os
sys.path.insert(0, os.getcwd())
import services.mapping.constants as constants 
import spacy
from spacy.tokens import Doc
from common.knowledge_base import LITERAL_DATATYPES, ResourceType
class TypeMapper(object):
    '''
    Class that finds knowledge base types (classes) corresponding to small texts.

    It stores a lexicon of type labels and their corresponding KB URL.
    In case the lexicon does not contain the queried text, the most probable type is
    computed via semantic similarity.

    e.g.
    "producers" -> ['http://dbpedia.org/class/yago/Producer110480018', 'http://dbpedia.org/ontology/productionCompany']

    
    '''
    def __init__(self):
        self.lemmatizer = nltk.wordnet.WordNetLemmatizer()
        self.label_vs_classes = {}
        self.label_vs_doc = {}

        print("Loading spacy...")
        self.spacy = spacy.load('en_core_web_lg')

        if not os.path.exists(constants.TYPE_LEXICON_PATH) or not os.path.exists(constants.LABELS_SPACY_DOCS_PATH):
            print("No type lexicon was found. Generating it at {}".format(constants.TYPE_LEXICON_PATH))
            self.__generate_lexicon()
        else:
            with open(constants.TYPE_LEXICON_PATH, 'r', encoding='utf-8') as file:
                for line in tqdm(file.readlines(), desc="Loading type lexicon"):
                    line = line.replace('\n', '')
                    label, urls = line.split('\t')
                    self.label_vs_classes[label] = urls.split(' ')
            with open(constants.LABELS_SPACY_DOCS_PATH, 'r', encoding='utf-8') as file:
                docs = json.load(file)
                self.label_vs_doc = {label: Doc(self.spacy.vocab).from_bytes(codecs.decode(bytes(doc_bytes_str, 'utf-8'), encoding='base64')) for label, doc_bytes_str in tqdm(docs.items(), desc='Loading label spacy docs')}

    
    def __call__(self, type_string: str):
        best_types = []

        lemmatized = ' '.join([self.lemmatizer.lemmatize(word) for word in type_string.split()])

        if type_string in self.label_vs_classes:
            return list(self.label_vs_classes[type_string])
        elif lemmatized in self.label_vs_classes:
            return list(self.label_vs_classes[lemmatized])
        else: 
            '''
            String not found in the lexicon, we pick the best constants.TOP_N_SIMILAR_TYPES types by semantic similarity
            We pick more than one because similarity is not such a reliable metric, so it should be more relaxed => more possible types
            '''
            type_string_doc = self.spacy(type_string)
            if not type_string_doc.vector_norm:
                # Can't compute vector for the type string
                return []
            similarities = [(label, label_doc.similarity(type_string_doc)) for label, label_doc in self.label_vs_doc.items() if label_doc.vector_norm]
            similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
            for i in range(constants.TOP_N_SIMILAR_TYPES):
                best_types.extend(self.label_vs_classes[similarities[i][0]])

        return best_types

    def __get_similarity(self, internal_label, phrase):
        # Get the similarity between a label that's part of the lexicon and an arbitrary phrase
        label_doc = self.label_vs_doc[internal_label]
        phrase_doc = self.spacy(phrase)
        return label_doc.similarity(phrase_doc)

    def __generate_lexicon(self):
        def label_from_yago_url(url: str) -> str:
            return re.sub("([a-z])([A-Z])","\g<1> \g<2>", re.sub(r'[0-9]+', '', url.replace('<http://dbpedia.org/class/yago/', '').replace('>', '').replace('<', ''))).lower()

        def label_from_dbpedia_url(url: str) -> str:
            return re.sub("([a-z])([A-Z])","\g<1> \g<2>", url.replace('<http://dbpedia.org/ontology/', '').replace('>', '').replace('<', '')).lower()
        
        
        # Adding hardcoded types for question words: "who" -> person, "when" -> datetime, "where" -> place, "how many" -> number
        self.label_vs_classes['who'] = IndexedSet(['http://dbpedia.org/ontology/Person', 'http://dbpedia.org/ontology/Organisation'])
        self.label_vs_classes['where'] = IndexedSet(['http://dbpedia.org/ontology/Place'])
        self.label_vs_classes['when'] = IndexedSet(LITERAL_DATATYPES[ResourceType.DATE])
        self.label_vs_classes['how many'] = IndexedSet(LITERAL_DATATYPES[ResourceType.NUMERAL])
        
        # Reading type labels from DBPedia type instances dataset
        with open(constants.DBPEDIA_TYPE_INSTANCES_PATH, 'r', encoding='utf-8') as infile:
            for line in tqdm(infile, desc="Loading DBPedia types:"):
                try:
                    _, _, o, _ = line.split(' ')
                    if 'ontology' in o:
                        label = label_from_dbpedia_url(o)
                        url = o.replace('>', '').replace('<', '')
                        if label not in self.label_vs_classes:
                            self.label_vs_classes[label] = IndexedSet([url])
                        else:
                            self.label_vs_classes[label].add(url)
                except:
                    pass

        # Reading type labels from YAGO taxonomy dataset
        with open(constants.YAGO_TAXONOMY_PATH, 'r', encoding='utf-8') as infile:
            for line in tqdm(infile, desc="Loading YAGO types"):
                try:
                    _, _, o, _ = line.split(' ')
                    label = label_from_yago_url(o)
                    url = o.replace('>', '').replace('<', '')
                    if label not in self.label_vs_classes:
                        self.label_vs_classes[label] = IndexedSet([url])
                    else:
                        self.label_vs_classes[label].add(url)
                except:
                    pass

        # Reading type labels from wordnet synonyms dataset
        with open(constants.DBPEDIA_TYPE_SYNSETS_PATH, 'r', encoding='utf-8') as file:
            for line in tqdm(file):
                try:
                    url, synset = line.split(',')
                    if synset == '\n':
                        continue
                    url = url.replace('>', '').replace('<','')
                    labels = [label.replace('_', ' ').replace('\n', '') for label in synset.split(' ')]
                    for label in labels:
                        if label not in self.label_vs_classes:
                            self.label_vs_classes[label] = IndexedSet([url])
                        else:
                            self.label_vs_classes[label].add(url)
                except:
                    pass
        
        # Dumping the lexicon
        with open(constants.TYPE_LEXICON_PATH, 'w', encoding='utf-8') as file:
            for label, uris in self.label_vs_classes.items():
                file.write(label + '\t' + ' '.join(uris) + '\n')

        # We also need to compute the spacy docs for the labels
        with open(constants.LABELS_SPACY_DOCS_PATH, 'w', encoding='utf-8') as file:
            label_vs_serialized_doc = {} 
            for label in tqdm(self.label_vs_classes.keys(), desc='Precomputing label spacy docs'):
                doc = self.spacy(label)
                self.label_vs_doc[label] = doc
                label_vs_serialized_doc[label] = str(codecs.encode(doc.to_bytes(), encoding='base64'), encoding='utf-8')
            json.dump(label_vs_serialized_doc, file)

# mapper = TypeMapper()