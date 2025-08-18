import os
import sys
import time
from multiprocessing import Process
from spiders.fii_spider import run_fii
from spiders.acao_spider import run_scraper

def run_fii_spider():
    """Run the FII spider in a separate process"""
    print("\n" + "="*50)
    print("Iniciando coleta de FIIS...")
    print("="*50)
    run_fii()
    print("\n" + "="*50)
    print("Coleta de FIIS concluída!")
    print("="*50)

def run_acao_spider():
    """Run the Ação spider in a separate process"""
    print("\n" + "="*50)
    print("Iniciando coleta de Ações...")
    print("="*50)
    run_scraper()
    print("\n" + "="*50)
    print("Coleta de Ações concluída!")
    print("="*50)

def main():

    fii_process = Process(target=run_fii_spider)
    fii_process.start()
    fii_process.join()

    time.sleep(2)

    acao_process = Process(target=run_acao_spider)
    acao_process.start()
    acao_process.join() 

    print("\n" + "="*50)
    print("Todas as coletas foram concluídas com sucesso!")
    print("="*50)

if __name__ == "__main__":
    main()