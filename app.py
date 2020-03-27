import subprocess
import sys
import os

def run_services():
    services = []
    
    services.append(subprocess.Popen(['python', r'services\nlp\run_nlp_serivce.py']))
    services.append(subprocess.Popen(['python', r'services\parser\run_parser_service.py']))
    services.append(subprocess.Popen(['python', r'services\mapping\run_mapping_service.py']))
    services.append(subprocess.Popen(['python', r'services\query_generator\run_query_generation_service.py']))
    services.append(subprocess.Popen(['python', r'services\knowledge_base\run_knowledge_base_service.py']))
    
    return services

def main():
    _ = run_services()

    # os.chdir('app')
    # subprocess.call(['npm', 'start'], shell=True)
    

if __name__ == '__main__':
    main()
    # app = connexion.App(__name__, 1000, specification_dir='swagger/')
    # app.add_api('qald.yaml', resolver=RestyResolver('api'))
    # app.run()
