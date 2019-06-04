import os
import sys
import time
import re
import spacy
from typing import List
from pytorch_pretrained_bert.tokenization import BertTokenizer

sys.path.insert(0, os.getcwd())
from services.nlp.constants import BERT_MODEL
from common.constants import DO_LOWERCASE

TOKENIZER = BertTokenizer.from_pretrained(BERT_MODEL, do_lower_case=DO_LOWERCASE)
SPACY_NLP = spacy.load('en_core_web_lg')

def tokenize(text: str) -> List[str]:
    return TOKENIZER.tokenize(text)

def spacy_process(text: str) -> dict:
    doc = SPACY_NLP(text)
    result = {
        'pos':    [token.pos_ for token in doc],
        'dep':    [token.dep_ for token in doc],
        'tokens': [token.text for token in doc],
        'idx':    [token.idx for token in doc],
    }
    return result

def pos_tag(text: str) -> List[str]:
    return pos_tags

def remove_punctuation(text: str) -> List[str]:
    return re.sub(r'[^\w-]', ' ', text)
    