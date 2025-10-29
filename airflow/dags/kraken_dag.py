from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from pendulum import datetime
import pandas as pd
import os
#from scraper.scraper.pipelines import main
from include.scraper.scraper.spiders.acao_spider import run_scraper
#from scraper.scraper.spiders.fii_fundsexplorer_spider import run_fii_fundsexplorer
from include.scraper.scraper.spiders.fii_investidor_spider import run_fii

@dag(
    start_date=datetime(2024, 1, 1),
    schedule='0 9-18 * * 1-5',
    catchup=False,
    default_args={"owner": "Astro", "retries": 1},
    tags=["database", "setup", "postgres", "sql"],
    template_searchpath='/usr/local/airflow/include/scripts/'
)
def kraken_test():
    
    # Criar os schemas bronze, silver e gold
    # Nota: Esta task usa a conexão 'airflowteste' que você configurou
    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='airflowteste',
        sql='create_tables.sql',
    )

    crawl_acoes = PythonOperator(
        task_id='crawl_acoes',
        python_callable=run_scraper,
    )

    crawl_fiis_investidor = PythonOperator(
        task_id='crawl_fiis_investidor',
        python_callable=run_fii,
    )

    @task
    def upsert_csv_to_bronze():
        """
        Faz UPSERT dos dados dos CSVs para as tabelas do schema bronze.
        Usa ON CONFLICT para atualizar registros existentes baseado no campo 'papel'.
        """
        
        # Mapeamento: arquivo CSV -> tabela no schema bronze
        csv_table_mapping = {
            '/usr/local/airflow/include/data/fiis_kpis.csv': 'bronze.fiis_kpi',
            '/usr/local/airflow/include/data/fiis_info.csv': 'bronze.fiis_info',
            '/usr/local/airflow/include/data/acoes_kpi.csv': 'bronze.acoes_kpi',
            '/usr/local/airflow/include/data/acoes_indicadores.csv': 'bronze.acoes_indicadores',
            '/usr/local/airflow/include/data/acoes_info.csv': 'bronze.acoes_info',
            '/usr/local/airflow/include/data/acoes_img.csv': 'bronze.acoes_img',

        }

        
        
        # Conectar ao PostgreSQL
        hook = PostgresHook(postgres_conn_id='airflowteste')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        for csv_file, table_name in csv_table_mapping.items():
            csv_path = f'{csv_file}'
            
            # Verificar se o arquivo existe
            if not os.path.exists(csv_path):
                print(f"⚠ Arquivo não encontrado: {csv_path}")
                continue
            
            print(f"\n📊 Processando: {csv_file} -> {table_name}")
            
            # Ler CSV
            df = pd.read_csv(csv_path)
            print(f"   Linhas no CSV: {len(df)}")
            print(f"   Colunas no CSV: {list(df.columns)}")
            
            if len(df) == 0:
                print(f"   ⚠ CSV vazio, pulando...")
                continue
            
            # Normalizar nomes das colunas do CSV (lowercase, remover espaços)
            #df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
            
            # Obter colunas da tabela (exceto id e data_atualizacao)
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = '{table_name.split('.')[0]}' 
                AND table_name = '{table_name.split('.')[1]}'
                AND column_name NOT IN ('id', 'data_atualizacao')
                ORDER BY ordinal_position
            """)
            db_columns = [row[0] for row in cursor.fetchall()]
            print(f"   Colunas no DB: {db_columns}")
            
            # Filtrar apenas colunas que existem no CSV e no DB
            common_columns = [col for col in db_columns if col in df.columns]
            
            if len(common_columns) == 0:
                print(f"   ⚠ Nenhuma coluna em comum encontrada, pulando...")
                continue
                
            df_filtered = df[common_columns]
            
            print(f"   Colunas em comum: {common_columns}")
            
            # Construir query UPSERT
            columns_str = ', '.join(common_columns)
            placeholders = ', '.join(['%s'] * len(common_columns))
            
            # UPDATE clause para ON CONFLICT
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in common_columns if col != 'papel'])
            
            upsert_query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT (papel) 
                DO UPDATE SET {update_clause}, data_atualizacao = CURRENT_TIMESTAMP
            """
            
            # Inserir dados linha por linha (para datasets pequenos)
            inserted = 0
            updated = 0
            
            for _, row in df_filtered.iterrows():
                try:
                    cursor.execute(upsert_query, tuple(row))
                    if cursor.rowcount > 0:
                        inserted += 1
                    else:
                        updated += 1
                except Exception as e:
                    print(f"   ⚠ Erro na linha: {e}")
                    continue
            
            conn.commit()
            print(f"   ✓ Inseridos: {inserted}, Atualizados: {updated}")
        
        cursor.close()
        conn.close()
        
        print("\n✓ UPSERT concluído para todas as tabelas!")
    
    # Definir dependências
    create_tables >>  [crawl_acoes, crawl_fiis_investidor] >> upsert_csv_to_bronze()

# Instanciar o DAG
kraken_test()
