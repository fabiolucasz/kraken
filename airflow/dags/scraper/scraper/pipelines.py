import time
from multiprocessing import Process
from spiders.fii_investidor_spider import run_fii
from spiders.acao_spider import run_scraper
from spiders.fii_fundsexplorer_spider import run_fii_fundsexplorer
import schedule


def run_fii_spider():
    """Run the FII spider in a separate process"""
    print("\n" + "="*50)
    print("Iniciando coleta de FIIS...")
    print("="*50)
    run_fii()
    print("\n" + "="*50)
    print("Coleta de FIIS concluída!")
    print("="*50)

def run_fii_fundsexplorer_spider():
    """Run the FII spider in a separate process"""
    print("\n" + "="*50)
    print("Iniciando coleta de FIIS do FUNDSEXPLORER...")
    print("="*50)
    run_fii_fundsexplorer()
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

    fii_fundsexplorer_process = Process(target=run_fii_fundsexplorer_spider)
    fii_fundsexplorer_process.start()
    fii_fundsexplorer_process.join()

    time.sleep(2)

    acao_process = Process(target=run_acao_spider)
    acao_process.start()
    acao_process.join() 

    print("\n" + "="*50)
    print("Todas as coletas foram concluídas com sucesso!")
    print("="*50)




if __name__ == "__main__":
    import datetime
    
    def is_time_between(start, end, now=None):
        now = now or datetime.datetime.now().time()
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end

    if is_time_between(datetime.time(10, 0), datetime.time(18, 0)):
        main()

    for hour in range(10, 18):
        schedule.every().day.at(f"{hour:02d}:00").do(main)

    while True:
        current_time = datetime.datetime.now().time()
        if is_time_between(datetime.time(10, 0), datetime.time(18, 0)):
            schedule.run_pending()
        time.sleep(60)