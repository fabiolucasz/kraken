from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from pendulum import datetime
from scraper.scraper.spiders.fii_funds import start_crawl
#from scraper.scraper.spiders.acao_spider import run_scraper
#from scraper.scraper.spiders.fii_funds import run_fii_fundsexplorer
#from scraper.scraper.spiders.fii_investidor_spider import run_fii

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Fabio", "retries": 1},
    tags=["database", "setup", "postgres", "sql"]
)
def kraken_playwright():

    crawl_fiis_fundsexplorer = PythonOperator(
        task_id='crawl_fiis_fundsexplorer',
        python_callable=start_crawl,
    )

    # by_bash = BashOperator(
    #     task_id='by_bash',
    #     bash_command='cd scraper/scraper/spiders && python3 fii_funds.py',
    # )

    
    
    # Definir dependências
    crawl_fiis_fundsexplorer

# Instanciar o DAG
kraken_playwright()
