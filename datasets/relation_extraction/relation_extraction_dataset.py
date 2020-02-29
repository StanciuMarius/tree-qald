
import torch
import json
from torch.utils.data import Dataset, DataLoader

DATASET_PATHS = [
    # r'datasets\relation_extraction\fewrel\data\train_normalized.json',
    # r'datasets\relation_extraction\NYT10\data\train_normalized.json',
    # r'datasets\relation_extraction\simple_questions\data\simple_normalized_train.json',
    r'datasets\relation_extraction\tacred\data\train_normalized.json',
]

class RelationExtractionDataset(Dataset):
    def __init__(self, transform=None):
        self.transform = transform
        
        self.examples = []
        for path in DATASET_PATHS:
            with open(path, 'r', encoding='utf-8') as file:
                file_examples = json.load(file)[:5000]
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
