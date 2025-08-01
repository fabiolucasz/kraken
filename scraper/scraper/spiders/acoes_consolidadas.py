import pandas as pd
import os

def merge_acoes():
    # Lista de DataFrames que serão unidos
    dataframes_indicadores = []
    dataframes_info = []
    dataframes_kpi = []

    # Lê a lista de papéis
    acoes = pd.read_csv('acoes-listadas-b3.csv', quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

    for papel in acoes['Ticker']:
        arquivo_indicadores = f'data_csv/{papel}_indicadores.csv'
        arquivo_info = f'data_csv/{papel}_info.csv'
        arquivo_kpi = f'data_csv/{papel}_kpi.csv'
        
        if os.path.exists(arquivo_indicadores) and os.path.exists(arquivo_info) and os.path.exists(arquivo_kpi):
            try:
                df_indicadores = pd.read_csv(arquivo_indicadores, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
                df_info = pd.read_csv(arquivo_info, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
                df_kpi = pd.read_csv(arquivo_kpi, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
                dataframes_indicadores.append(df_indicadores)
                dataframes_info.append(df_info)
                dataframes_kpi.append(df_kpi)
                print(f"{papel} lido com sucesso")
            except Exception as e:
                print(f"Erro ao ler {papel}: {e}")
        else:
            print(f"Arquivo {papel} não encontrado")

    # Junta todos os DataFrames, preenchendo valores ausentes com ""
    if dataframes_indicadores:
        df_consolidado_indicadores = pd.concat(dataframes_indicadores, ignore_index=True).fillna("")
        df_consolidado_info = pd.concat(dataframes_info, ignore_index=True).fillna("")
        df_consolidado_kpi = pd.concat(dataframes_kpi, ignore_index=True).fillna("")
        df_consolidado_indicadores.to_csv("acoes_consolidadas_indicadores.csv", index=False, encoding='utf-8', sep=',')
        df_consolidado_info.to_csv("acoes_consolidadas_info.csv", index=False, encoding='utf-8', sep=',')
        df_consolidado_kpi.to_csv("acoes_consolidadas_kpi.csv", index=False, encoding='utf-8', sep=',')
        print("Arquivos consolidados salvo com sucesso!")
        remove_arquivos()
        return df_consolidado_indicadores, df_consolidado_info, df_consolidado_kpi
    else:
        print("Nenhum arquivo foi encontrado para consolidação.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def remove_arquivos():
    acoes = pd.read_csv('acoes-listadas-b3.csv', quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    for papel in acoes['Ticker']:
        arquivo_indicadores = f'data_csv/{papel}_indicadores.csv'
        arquivo_info = f'data_csv/{papel}_info.csv'
        arquivo_kpi = f'data_csv/{papel}_kpi.csv'
        if os.path.exists(arquivo_indicadores):
            os.remove(arquivo_indicadores)
        if os.path.exists(arquivo_info):
            os.remove(arquivo_info)
        if os.path.exists(arquivo_kpi):
            os.remove(arquivo_kpi)

merge_acoes()
