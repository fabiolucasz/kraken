from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from pendulum import datetime
from scraper.scraper.spiders.acao_spider import run_scraper
#from scraper.scraper.spiders.fii_funds import run_fii_fundsexplorer
from scraper.scraper.spiders.fii_investidor_spider import run_fii

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Fabio", "retries": 1},
    tags=["database", "setup", "postgres", "sql"]
)
def kraken_pipeline():

    crawl_acoes = PythonOperator(
        task_id='crawl_acoes',
        python_callable=run_scraper,
    )

    crawl_fiis_investidor = PythonOperator(
        task_id='crawl_fiis_investidor',
        python_callable=run_fii,
    )

    # crawl_fiis_fundsexplorer = PythonOperator(
    #     task_id='crawl_fiis_fundsexplorer',
    #     python_callable=run_fii_fundsexplorer,
    # )

    
    
    # Definir dependências
    [crawl_acoes, crawl_fiis_investidor]

# Instanciar o DAG
kraken_pipeline()
