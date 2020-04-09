
import json
import re
import os
import sys
sys.path.insert(0, os.getcwd())

from datasets.datasets import DatasetResolver

class YagoTaxonomyDataset(object):
    def __init__(self):
        self.parents = {}
        self.dataset_resolver = DatasetResolver()
        with open(self.dataset_resolver('yago-taxonomy', 'taxonomy'), 'r', encoding='utf-8') as file:
            max_parents = 1
            for line in file: 
                try:
                    subject, _, object, _ = line.split()
                    subject = subject[1:-1]
                    object = object[1:-1]
                    if subject in self.parents:
                        self.parents[subject].add(object)
                    else:
                        self.parents[subject] = {object}
                except:
                    pass

    def is_subclass(self, subclass, superclass):
        if subclass == superclass: return True
        if not subclass in self.parents: return False

        parents = self.parents[subclass]
        for parent in parents:
            if self.is_subclass(parent, superclass): return True
        return False

    def label_for_class(self, url):
        url = url.replace('http://dbpedia.org/class/yago/', '') 
        url = re.sub(r'[0-9]+', '', url)
        url = re.sub("([a-z])([A-Z])","\g<1> \g<2>", url) # CamelCase to separate words
        return url.lower()
        
    def __test__(self):
        assert self.is_subclass('http://dbpedia.org/class/yago/Saint110546850', 'http://dbpedia.org/class/yago/Person100007846') == True
        assert self.is_subclass('http://dbpedia.org/class/yago/GoodWord106643120', 'http://dbpedia.org/class/yago/Message106598915') == True
    

if __name__ == '__main__':
    yago = YagoTaxonomyDataset()
    yago.__test__()
    print("All tests were successful!")

