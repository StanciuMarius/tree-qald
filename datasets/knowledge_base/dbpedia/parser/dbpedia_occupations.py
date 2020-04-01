
import json
import re
OCCUPATIONS_DATASET_PATH = r'datasets\knowledge_base\dbpedia\data\occupation titles.json'

class DBPediaOccupationsDataset(object):
    def __init__(self):
        self.occupations = set()
        with open(OCCUPATIONS_DATASET_PATH, 'r', encoding='utf-8') as file:
            content = json.load(file)
            texts = [binding['title']['value'] for binding in content['results']['bindings']]
            
            for text in texts:
                occupations = re.split(r'[,&/]|(and)', text)
                occupations = [w.strip().lower() for w in occupations if w]
                self.occupations.update(occupations)
