import re


from tqdm import tqdm
from boltons.setutils import IndexedSet

import sys
import os
sys.path.insert(0, os.getcwd())
from services.mapping.constants import TYPE_LEXICON_PATH, YAGO_TAXONOMY_PATH, DBPEDIA_TYPE_INSTANCES_PATH

class TypeMapping(object):
    '''
    Class that finds knowledge base types (classes) corresponding to small texts.

    It stores a lexicon of types in a dictionary.
    The lexicon contains the text of the kb types. 

    In case the lexicon does not contain the queried text, the most probable is
    computed via semantic similarity and synonyms.

    E.g. "French" -> "dbpedia.org/resource/France"
    E.g. "Obama" -> "dbpedia.org/resource/Barack_Obama"
    '''
    def __init__(self, lexicon_path: str):
        self.label_vs_classes = {}

        if not os.path.exists(lexicon_path):
            print("No type lexicon was found. Generating it at {}".format(lexicon_path))
            self.__generate_lexicon(lexicon_path)
        else:
            with open(lexicon_path, 'r', encoding='utf-8') as file:
                for line in file:
                    label, urls = line.split('\t')
                    self.label_vs_classes[label] = urls.split(' ')


    def __generate_lexicon(self, lexicon_path: str):
        def label_from_yago_url(url: str) -> str:
            return re.sub("([a-z])([A-Z])","\g<1> \g<2>", re.sub(r'[0-9]+', '', url.replace('<http://dbpedia.org/class/yago/', '').replace('>', '').replace('<', ''))).lower()

        def label_from_dbpedia_url(url: str) -> str:
            return re.sub("([a-z])([A-Z])","\g<1> \g<2>", url.replace('<http://dbpedia.org/ontology/', '').replace('>', '').replace('<', '')).lower()
        
        # Reading type labels from DBPedia type instances dataset
        with open(DBPEDIA_TYPE_INSTANCES_PATH, 'r', encoding='utf-8') as infile:
            label_vs_class = {}
            for line in tqdm(infile):
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
        with open(YAGO_TAXONOMY_PATH, 'r', encoding='utf-8') as infile:
            label_vs_class = {}
            for line in tqdm(infile):
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
            
        with open(lexicon_path, 'w', encoding='utf-8') as file:
            for label, uris in self.label_vs_classes.items():
                file.write(label + '\t' + ' '.join(uris) + '\n')

TypeMapping(TYPE_LEXICON_PATH)