
import torch
import json
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple
import sys
import os
sys.path.insert(0, os.getcwd())

from datasets.datasets import DatasetResolver
from datasets.relation_extraction.fewrel.normalize_fewrel import normalize_fewrel
from datasets.relation_extraction.tacred.normalize_tacred import normalize_tacred
from datasets.relation_extraction.simple_questions.normalize_simplequestions import normalize_simplequestions
from datasets.relation_extraction.NYT10.normalize_nyt10 import normalize_nyt10
from datasets.parsing.normalize_treeqald import normalize_treeqald

class RelationExtractionDataset(Dataset):
    def __init__(self, files=List[Tuple], transform=None):
        self.transform = transform
        self.dataset_resolver = DatasetResolver()
        self.examples = []
        
        for dataset_name, file_name in files:
            original_path = self.dataset_resolver(dataset_name, file_name)

            # Process the original downloaded datasets and bring them to a common format
            if dataset_name == 'tacred': normalized_path = normalize_tacred(original_path)
            elif dataset_name == 'fewrel': normalized_path = normalize_fewrel(original_path)
            elif dataset_name == 'nyt10': normalized_path = normalize_nyt10(original_path)
            elif dataset_name == 'simplequestions': normalized_path = normalize_simplequestions(original_path)
            elif dataset_name == 'tree-qald': normalized_path = normalize_treeqald(original_path)

            with open(normalized_path, 'r', encoding='utf-8') as file:
                file_examples = json.load(file)
                self.examples.extend(file_examples)
        self.labels = list(set([example['relation'] for example in self.examples]))
        self.label_vs_id = {label: label_id for label_id, label in enumerate(self.labels)}

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()[0]
        sample = self.examples[idx]

        if self.transform:
            sample = self.transform(sample)
                    
        return sample
