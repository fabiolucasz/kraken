import os
import pandas as pd

#path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
data_dir = os.path.join(base_dir, 'include', 'dbt_dw', 'kraken_dw', 'seeds')

#ler csv
df = pd.read_csv(os.path.join(data_dir, 'fiis_info.csv'))

#mostrar unicas
print(df['valor_patrimonial_unidade'].unique())

#contar nulos
print(df['valor_patrimonial_unidade'].isnull().sum())