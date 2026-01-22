from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pendulum import datetime
from include.scraper.scraper.spiders.acao_spider import run_scraper
from include.scraper.scraper.spiders.fii_investidor_spider import run_fii
from airflow.models import Variable

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Fabio", "retries": 1},
    tags=["database", "setup", "postgres", "sql"]
)
def kraken_pipeline():
    dbt_env = Variable.get("dbt_env", default_var="dev").lower()
    crawl_acoes = PythonOperator(
        task_id='crawl_acoes',
        python_callable=run_scraper,
    )

    crawl_fiis_investidor = PythonOperator(
        task_id='crawl_fiis_investidor',
        python_callable=run_fii,
    )

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    trigger_pipeline = TriggerDagRunOperator(
        task_id='trigger_pipeline',
        trigger_dag_id=f'dag_kraken_dw_{dbt_env}',  
        wait_for_completion=False,  
        reset_dag_run=True,         
        poke_interval=60            
    )

    start >> [crawl_acoes, crawl_fiis_investidor] >> end >> trigger_pipeline
    return trigger_pipeline

kraken_pipeline()
