import os
import sys
from typing import List

sys.path.insert(0, os.getcwd())
from common.query_tree import QueryTree
from common.query_tree import SerializationFormat
from services.tasks import run_task, Task

INTERMEDIATE_QUERY         = r'services\parser\tmp\intermediate_input_query.seq_lu'
MODEL_PATH                 = r'services\parser\tmp\model\ptb-bilstm2-chlstm-glove'
INTERMEDIATE_OUTPUT        = r'services\parser\tmp\intermediate_output.paran'
NCRFPP_PATH                = r'services\parser\tree2labels\NCRFpp'

question = 'Who is the wife of Barack Obama?'
tokens = run_task(Task.TOKENIZE, question)
with open(INTERMEDIATE_QUERY, 'w') as intermediate_output_file:
    intermediate_output_file.write('-BOS-\t-BOS-\t-BOS-\n')
    for token in tokens:
        intermediate_output_file.write(token + '\tTOKEN\tUNUSED\n')
    intermediate_output_file.write('-EOS-\t-EOS-\t-EOS-\n')


parse_command = 'python ./services/parser/tree2labels/run_ncrfpp.py --test {INPUT} --model {MODEL} --status test --gpu False --output {OUTPUT} --ncrfpp {NCRFPP}'
parse_command = parse_command.format(INPUT=INTERMEDIATE_QUERY, MODEL=MODEL_PATH, OUTPUT=INTERMEDIATE_OUTPUT, NCRFPP=NCRFPP_PATH)
os.system(parse_command)

# // "args": [
# //     "--test",
# //     ".\\outputyo\\yolanda-test.seq_lu",
# //     "--gold",
# //     ".\\test.txt",
# //     "--model",
# //     ".\\tmp\\ptb-bilstm2-chlstm-glove",
# //     "--status",
# //     "test",
# //     "--gpu",
# //     "False",
# //     "--output",
# //     ".\\outputs",
# //     "--evalb",
# //     ".\\EVALB\\evalb",
# //     "--ncrfpp",
# //     "NCRFpp",
# // ]