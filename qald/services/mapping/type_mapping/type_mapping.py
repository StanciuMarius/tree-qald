import sys
import os
import pickle
import json
import nltk
import pygtrie
import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab

sys.path.insert(0, os.getcwd())
from services.mapping.constants import TYPE_IMPORTANCE_PATH, TYPE_SYNONYMS_PATH, TYPE_SIMILARITIES_PATH, TYPES_TRIE_PATH, SPACY_CACHE_PATH


from services.tasks import run_task, Task
# Using local SPACY for faster processing

print ("Loading Spacy (en_core_web_lg)...")
SPACY_NLP = spacy.load('en_core_web_lg')

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

    def __init__(self):
        self.allTypes = {}
        self.L = nltk.wordnet.WordNetLemmatizer()
        self.trie_1, self.trie_2 = self._load_data()
        self.spacy_cache = {}

    def get_similarity(self, phrase1: str, phrase2: str):
        """ Get the similarity between two phrases using spacy."""
        def spacy_similarity(self, text_a: str, text_b: str):
            if text_a not in self.spacy_cache:
                self.spacy_cache[text_a] = SPACY_NLP(text_a)
            doc_a = self.spacy_cache[text_a]
            
            if text_b not in self.spacy_cache:
                self.spacy_cache[text_b] = SPACY_NLP(text_b)
            doc_b = self.spacy_cache[text_b]

            try:
                return doc_a.similarity(doc_b)
            except:
                print('Error in getting spacy similarity for %s: %s' %(a, b))
            return 0.0


        phrase1 = self._get_type_from_resource(phrase1)
        phrase1_with_spaces = ''
        phrase1_with_spaces += phrase1[0]

        for i in range(1, len(phrase1)):
            if ord(phrase1[i]) < 97:
                phrase1_with_spaces += ' '
            phrase1_with_spaces += phrase1[i]

        return spacy_similarity(self, phrase1_with_spaces, phrase2)
        # return self.spacy_nlp(phrase1_with_spaces).similarity(self.spacy_nlp(phrase2))

    def get_best_types(self, query_string):
        """ Method that gets the best matches for a query.

        It gets the query string for the entity and returns a list with the best
        types found matching the string.

        TODO(eugenv): update the comments.
        """

        original = query_string
        best_types = []

        words = query_string.split()
        query_string = ''
        for word in words:
            query_string += self.L.lemmatize(word)

        if query_string.replace(" ", "").lower() in self.trie_1:
            query_string = query_string.replace(" ", "").lower()

            types = sorted(self.trie_1[query_string].items(),
                    key=lambda kb: (-kb[1], kb[0]))
            for short_type, score in types:
                best_types.append(self._get_resource_from_type(short_type))
                break
        elif query_string.replace(" ", "").lower() in self.trie_2:
            query_string = query_string.replace(" ", "").lower()

            types = sorted(self.trie_2[query_string].items(),
                    key=lambda kb: (-kb[1], kb[0]))
            for short_type, score in types:
                best_types.append(self._get_resource_from_type(short_type))
                break
        else:
            L = []
            for key, res in self.allTypes.items():
                L.append((self.get_similarity(res, original), res))
            L = sorted(L, key=lambda tup: -tup[0])

            return [L[0][1]]

        return best_types

    def teest(self, query_string):
        " NOT IMPORTANT. """

        for x,y in self.trie.items():
            print (x, y)

    def _get_resource_from_type(self, type_text):
        """TODO: add comments"""
        
        return "http://dbpedia.org/ontology/" + type_text

    def _get_type_from_resource(self, url):
        """TODO: add comments"""

        return url[url.find('ontology') + 9:]

    def _save_trie(self, trie, filename):
        """TODO: add comments"""

        with open(filename, "wb") as f:
            pickle.dump(trie, f)

    def _load_data(self):
        """TODO: add comments"""

        if os.path.isfile(TYPES_TRIE_PATH):
            print("Loading trie from %s" % TYPES_TRIE_PATH)

            with open(TYPES_TRIE_PATH, "rb") as f:
                data = pickle.load(f)
                (trie_1, trie_2, self.allTypes) = data
            print ("Done loading trie!")
            return (trie_1, trie_2)

        print("Building trie using importance from %s, synonyms from %s" %
                (TYPE_IMPORTANCE_PATH, TYPE_SYNONYMS_PATH))
        trie_1 = pygtrie.StringTrie(separator=os.path.sep)
        trie_2 = pygtrie.StringTrie(separator=os.path.sep)
    
        self._load_types(TYPE_IMPORTANCE_PATH, trie_1)
        self._load_synonyms(TYPE_SYNONYMS_PATH, trie_2, trie_1)
        self._load_similarities(TYPE_SIMILARITIES_PATH, trie_2, trie_1)

        data = (trie_1, trie_2, self.allTypes)
        self._save_trie(data, TYPES_TRIE_PATH)
        return (trie_1, trie_2)

    def _get_importance(self, type_text, trie):
      
        query = type_text.lower()
        if query in trie and type_text in trie[query]:
            return trie[query][type_text]
        return 1


    def _addTrieEntry(self, query, short_type, importance, trie):
        """TODO: add comments"""
        
        if query not in trie:
            trie[query] = {}

        trie[query][short_type] = importance


    def _load_types(self, importance_table, trie):
        """TODO: add comments"""

        if not os.path.isfile(importance_table):
            print("Importance table does not exist: %s" % importance_table)
            return

        with open(importance_table) as data_file:
            data = json.load(data_file)

            bindings = data['results']['bindings']
            for binding in bindings:
                type_resource = binding['type']['value']
                short_type = self._get_type_from_resource(type_resource)
                score = int(binding['score']['value'])

                self._addTrieEntry(short_type.lower(), short_type, score, trie)

                self.allTypes[short_type.lower()] = type_resource


    def _load_synonyms(self, synonyms_table, trie, trie_aux):
        """TODO: add comments"""

        if not os.path.isfile(synonyms_table):
            print("Synonyms table does not exist: %s" % synonyms_table)
            return

        with open(synonyms_table) as data_file:
            data = data_file.readlines()

            cnt = 0
            while cnt < len(data):
                type_resource = data[cnt][:-1]
                type_text = self._get_type_from_resource(type_resource)
                cnt += 1
                nb_of_synonyms = int(data[cnt])
                cnt += 1
                score = self._get_importance(type_text, trie_aux)

                for i in range(nb_of_synonyms):
                    syn = data[cnt][:-1]
                    cnt += 1

                    self._addTrieEntry(syn.replace('_', '').lower(), type_text,
                            score, trie)


    def _load_similarities(self, similarities_table, trie, trie_aux):
        """TODO: add comments"""

        if not os.path.isfile(similarities_table):
            print("Similarities table does not exist: %s" % similarities_table)
            return

        with open(similarities_table) as data_file:
            data = data_file.readlines()

            cnt = 0
            while cnt < len(data):
                type_resource = data[cnt][:-1]
                type_text = self._get_type_from_resource(type_resource)
                cnt += 1
                nb_of_similarities = int(data[cnt])
                cnt += 1
                score = self._get_importance(type_text, trie_aux)

                for i in range(nb_of_similarities):
                    sim = data[cnt][:-1]
                    cnt += 1

                    self._addTrieEntry(sim.replace('_', '').lower(), type_text,
                            score, trie)


# type_mapping = TypeMapping()
# print(type_mapping.get_best_types('footbal player'))
# print(type_mapping.get_best_types('tennis player'))
# print(type_mapping.get_best_types('singer'))
# print("yo")