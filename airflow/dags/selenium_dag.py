from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from pendulum import datetime
import pandas as pd
import os
#from scraper.scraper.pipelines import main
from scraper.scraper.spiders.fii_fundsexplorer_spider import run_fii_fundsexplorer

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Astro", "retries": 1},
    tags=["database", "setup", "postgres", "sql"],
)
def fii_fundsexplorer_test():
    crawl_fiis_fundsexplorer = PythonOperator(
        task_id='crawl_fiis_fundsexplorer',
        python_callable=run_fii_fundsexplorer,
    )

    crawl_fiis_fundsexplorer

fii_fundsexplorer_test()
