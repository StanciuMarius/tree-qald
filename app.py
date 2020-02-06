import subprocess
import sys
import os

def run_services():
    services = []
    
    services.append(subprocess.Popen(['python', './services/parser/run_parser_service.py']))
    services.append(subprocess.Popen(['python', './services/nlp/run_nlp_serivce.py']))
    
    return services

def main():
    _ = run_services()

    os.chdir('app')
    subprocess.call(['npm', 'start'], shell=True)
    

if __name__ == '__main__':
    app = connexion.App(__name__, 1000, specification_dir='swagger/')
    app.add_api('qald.yaml', resolver=RestyResolver('api'))
    app.run()