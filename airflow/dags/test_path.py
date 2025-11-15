from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from pendulum import datetime
from include.scraper.scraper.spiders.acao_test import run_scraper_test


@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Fabio", "retries": 1},
    tags=["database", "setup", "postgres", "sql"]
)
def test_path():

    crawl_acoes = PythonOperator(
        task_id='crawl_acoes',
        python_callable=run_scraper_test,
    )
    
    
    # Definir dependências
    [crawl_acoes]

# Instanciar o DAG
test_path()
