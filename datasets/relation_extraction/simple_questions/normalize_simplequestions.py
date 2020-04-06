import os

# TODO: rewrite code. Lost this unfortunately. Uploaded the normalized simplequestions on git as a temporary workaround.
def normalize_simplequestions(source_path):
    file_name = os.path.basename(source_path)
    file_name = file_name.split('.')[0]
    output_path = os.path.join(r'datasets\relation_extraction\simple_questions\data', file_name + '_normalized.json')
    if os.path.exists(output_path): return output_path

    return output_path
