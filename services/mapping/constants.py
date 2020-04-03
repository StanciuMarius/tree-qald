PATTY_DBPEDIA_PARAPHRASES_FILE_PATH = 'datasets/relation_extraction/patty/data/dbpedia-relation-paraphrases.txt'
ENTITY_LEXICON_PATH = 'datasets/entity_mapping/data/entity_lexicon.tsv'
ENTITY_DISAMBIGUATIONS_DATASET_PATH = r'datasets\entity_mapping\data\disambiguations_lang=en.ttl'
ENTITY_REDIRECTS_DATASET_PATH = r'datasets\entity_mapping\data\redirects_lang=en.ttl'
TYPE_IMPORTANCE_PATH = "datasets/type_mapping/data/type_importance.json"
TYPE_SYNONYMS_PATH = "datasets/type_mapping/data/type_synonyms.txt"
TYPE_SIMILARITIES_PATH = "datasets/type_mapping/data/type_similarities.txt"
TYPES_TRIE_PATH = "datasets/type_mapping/data/types_trie.pkl"
SPACY_CACHE_PATH = "services/mapping/type_mapping/cache.dump"

DBPEDIA_RESOURCE_PREFIX = r'http://dbpedia.org/resource/'
TYPE_LEXICON_PATH = r'datasets\type_mapping\data\lexicon.tsv'
LABELS_SPACY_DOCS_PATH = r'datasets\type_mapping\data\labels_spacy_docs.json'
YAGO_TAXONOMY_PATH = r'datasets\type_mapping\data\yago_taxonomy.nt'
DBPEDIA_TYPE_INSTANCES_PATH = r'datasets\type_mapping\data\instance-types_lang=en.ttl'
DBPEDIA_TYPE_SYNSETS_PATH = r'datasets\type_mapping\data\type_synonyms.csv'
TOP_N_SIMILAR_TYPES = 3
PATTY_POS_VS_SPACY_POS = {
    '[[det]]': 'DET',
    '[[pro]]': 'PRO',
    '[[adj]]': 'ADJ',
    '[[num]]': 'NUM',
    '[[prp]]': 'PRP',
    '[[mod]]': 'MOD',
    '[[con]]': 'CON'
}
