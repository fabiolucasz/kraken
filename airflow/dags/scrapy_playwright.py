from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from pendulum import datetime
#from include.scraper.scraper.spiders.acao_spider import run_scraper
from include.scraper.scraper.spiders.funds_scrapy import main
#from include.scraper.scraper.spiders.fii_investidor_spider import run_fii

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Fabio", "retries": 1},
    tags=["database", "setup", "postgres", "sql"]
)
def kraken_scrapy_playwright():


    crawl_fiis_fundsexplorer = PythonOperator(
        task_id='crawl_fiis_fundsexplorer',
        python_callable=main,
    )

    
    
    # Definir dependências
    crawl_fiis_fundsexplorer

# Instanciar o DAG
kraken_scrapy_playwright()
