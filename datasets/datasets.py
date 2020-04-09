import json
import os
from tqdl import download
from tqdm import tqdm
import bz2
import tarfile
from zipfile import ZipFile 

DATASET_METADATA_FILE_PATH = r'datasets\datasets.json'

class DatasetResolver(object):
    '''
        Automatically download, extract and resolve file paths from datasets based on the metadata from DATASET_METADATA_FILE_PATH.
    '''
    def __init__(self):
        with open(DATASET_METADATA_FILE_PATH, 'r', encoding='utf-8') as file:
            self.metadata = {metadata['name']: metadata for metadata in json.load(file)}
    
    def __call__(self, dataset_name: str, file_name: str) -> str:
        '''
            Retrieves the path of a file from within a dataset, as per DATASET_METADATA_FILE_PATH.
            If file is not found, the dataset is first downloaded and de-archived.
        '''
        if dataset_name not in self.metadata:
            raise Exception('Metadata for dataset {} not found in {}'.format(dataset_name, DATASET_METADATA_FILE_PATH))

        if file_name not in self.metadata[dataset_name]['files']:
            raise Exception('File {} not found in metadata for dataset {}'.format(file_name, dataset_name))
        
        file_path = self.metadata[dataset_name]['files'][file_name]

        if not os.path.exists(file_path):
            self.__download_dataset(dataset_name)
            self.__extract_archives(dataset_name)
            if not os.path.exists(file_path):
                raise Exception('Something went wrong downloading {} dataset'.format(dataset_name))
    
        return file_path

    def __download_dataset(self, dataset_name: str):
        if dataset_name == 'tacred':
            link_to_download_manually = self.metadata[dataset_name]['links'][0]
            file_to_download_manually = list(self.metadata[dataset_name]['archives'].items())[0][1]
            path_to_place_download = self.metadata[dataset_name]['download-path']
            raise Exception('Tacred does not have a public download link. You have to buy it and donwload it from this link {}. \
                After you are done, place the {} file in {}'.format(link_to_download_manually, file_to_download_manually, path_to_place_download))
        for link in self.metadata[dataset_name]['links']:
            file_name = link.split('/')[-1].replace('?dl=1', '').replace('?raw=true', '')
            path = os.path.join(self.metadata[dataset_name]['download-path'], file_name)
            print("Downloading {}:{}...".format(dataset_name, file_name))
            download(link, path)

    def __extract_archives(self, dataset_name: str):
        def extract_with_progress(archive_file, destination_path: str):
            try:
                members = archive_file.namelist()
            except:
                members = archive_file.getmembers()

            for member in tqdm(iterable=members, total=len(members)):
                archive_file.extract(member=member, path=destination_path)           


        # Nothing to extract
        if 'archives' not in self.metadata[dataset_name]: return

        for format, path in self.metadata[dataset_name]['archives'].items():
            print("Extracting {}...".format(path))
            if format in {'tar.gz', 'tgz'}:
                archive_file = tarfile.open(path)
                extract_with_progress(archive_file, self.metadata[dataset_name]['download-path'])
            elif format in {'zip'}:
                archive_file = ZipFile(path, 'r')
                extract_with_progress(archive_file, self.metadata[dataset_name]['download-path'])
            elif format in {'bz2'}:
                archive_file = bz2.open(path, "rb")
                with open(path.replace('.bz2', ''), 'wb') as file: file.write(archive_file.read())
            
            archive_file.close()

    def __test__(self):
        assert os.path.exists(self(dataset_name='simplequestions', file_name='validation'))
        assert os.path.exists(self(dataset_name='qald-8', file_name='train'))
        assert os.path.exists(self(dataset_name='qald-9', file_name='test'))
        assert os.path.exists(self(dataset_name='dbpedia-instance-types', file_name='types'))


if __name__ == '__main__':
    resolver = DatasetResolver()
    resolver.__test__()