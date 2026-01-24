import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
data_dir = os.path.join(base_dir, 'include', 'dbt_dw', 'kraken_dw', 'seeds')
acoes_info = pd.read_csv(os.path.join(data_dir, 'acoes_info.csv'))

df = pd.DataFrame(acoes_info)

#type of data on column all columns
print(df.dtypes)
