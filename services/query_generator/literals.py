from word2number import w2n as word2num
from num2words import num2words as num2word

ORDINAL_VS_NUM = {num2word(i, to='ordinal'): i for i in range(100)}

import re

def parse_number(text: str) -> int:
    text = text.strip()

    if re.search('[0-9]', text):
        # Trim ordinal suffix: 1st, 2nd, 3rd etc.
        text = text.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')

    # Full text ordinals
    if text in ORDINAL_VS_NUM:
        return ORDINAL_VS_NUM[text]

    return word2num.word_to_num(text)

