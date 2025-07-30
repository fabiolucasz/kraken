import pandas as pd
import os

def merge_acoes():
    # Lista de DataFrames que serão unidos
    dataframes = []

    # Lê a lista de papéis
    acoes = pd.read_csv('acoes-listadas-b3.csv', quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

    for papel in acoes['Ticker']:
        arquivo = f'data_csv/{papel}_indicadores.csv'
        if os.path.exists(arquivo):
            try:
                df = pd.read_csv(arquivo, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
                dataframes.append(df)
                print(f"{papel} lido com sucesso")
            except Exception as e:
                print(f"Erro ao ler {papel}: {e}")
        else:
            print(f"Arquivo {papel}_indicadores.csv não encontrado")

    # Junta todos os DataFrames, preenchendo valores ausentes com ""
    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True).fillna("")
        df_consolidado.to_csv("acoes_consolidadas.csv", index=False, encoding='utf-8', sep=',')
        print("Arquivo 'acoes_consolidadas.csv' salvo com sucesso!")
        return df_consolidado
    else:
        print("Nenhum arquivo foi encontrado para consolidação.")
        return pd.DataFrame()

merge_acoes()