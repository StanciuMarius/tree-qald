ENTITY_LEXICON_PATH = r'datasets\entity_mapping\data\entity_lexicon.tsv'
TYPE_LEXICON_PATH = r'datasets\type_mapping\data\lexicon.tsv'
DBPEDIA_RESOURCE_PREFIX = r'http://dbpedia.org/resource/'
LABELS_SPACY_DOCS_PATH = r'datasets\type_mapping\data\labels_spacy_docs.json'
TOP_N_SIMILAR_TYPES = 3

STOP_WORDS = {'pro', 'professional', 'known', 'popular', 'of', 'official', 'public'} # Words that tend to be useless for type mapping
PATTY_POS_VS_SPACY_POS = {
    '[[det]]': 'DET',
    '[[pro]]': 'PRO',
    '[[adj]]': 'ADJ',
    '[[num]]': 'NUM',
    '[[prp]]': 'PRP',
    '[[mod]]': 'MOD',
    '[[con]]': 'CON'
}
