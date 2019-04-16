import os
import sys
import time
from typing import List
from pytorch_pretrained_bert.tokenization import BertTokenizer

sys.path.insert(0, os.getcwd())
from services.nlp.constants import BERT_MODEL
from common.constants import DO_LOWERCASE

TOKENIZER = BertTokenizer.from_pretrained(BERT_MODEL, do_lower_case=DO_LOWERCASE)

def tokenize(text: str) -> List[str]:
    return TOKENIZER.tokenize(text)

    