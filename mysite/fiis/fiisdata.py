import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from sklearn.preprocessing import MinMaxScaler
import asyncio
import aiohttp
import pandas as pd
from .models import Fiis

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

liquidez_minima = 500_000
pvp_minimo = 0.70

def get_df1():
    url = 'https://www.fundamentus.com.br/fii_resultado.php'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    df = pd.read_html(StringIO(str(table)))[0]
    df.to_csv('./df1.csv', index=False)
    df = process_df1()
    df.to_csv('./df1.csv', index=False)
    return df

def process_df1():
    df = pd.read_csv("./df1.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    
    colunas_percentuais = ["FFO Yield", "Dividend Yield", "Cap Rate", "Vacância Média"]
    colunas_valores = ["Valor de Mercado", "Liquidez", "Preço do m2", "Aluguel por m2"]
    colunas_inteiras = ["Qtd de imóveis"]
    colunas_cotacao = ["Cotação"]
    colunas_pvp = ["P/VP"]

    for col in colunas_percentuais:
        df[col] = df[col].astype(str).str.replace("%", "", regex=False).str.replace(",", ".")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in colunas_valores:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in colunas_inteiras:
        df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

    for col in colunas_cotacao:
        df[col] = df[col].astype(str).str.replace(r"\D", "", regex=True)  
        df[col] = df[col].apply(
            lambda x: float(x.zfill(3)[:-2] + "." + x.zfill(3)[-2:]) if x else None
        )

    def pvp(x):
        x = x.strip()
        if not x.isdigit():
            return None
        if len(x) > 2:
            return float(x[:-2] + "." + x[-2:])
        else:
            return float("0." + x)

    for col in colunas_pvp:
        df[col] = df[col].astype(str).str.replace(r"\D", "", regex=True)
        df[col] = df[col].apply(pvp)
    df.to_csv('./df1.csv', index=False)
    
    return df


def rank_fiis():
    df = pd.read_csv("./final.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    
    # Indicadores relevantes
    indicadores = {
        'DY': 1,  # quanto maior, melhor
        'Liquidez': 0.5,      # quanto maior, melhor
        'Vacância': -1, # quanto menor, melhor
        'P/VP': -0.5           # quanto menor, melhor
    }

    # Remover nulos
    df = df.dropna(subset=indicadores.keys())

    scaler = MinMaxScaler()

    for col, peso in indicadores.items():
        # Normalizar entre 0 e 1
        norm = scaler.fit_transform(df[[col]])
        if peso < 0:
            norm = 1 - norm  # inverter se menor é melhor
        df[f'{col}_score'] = norm * abs(peso)

    # Rank final como soma ponderada dos scores
    df['Rank_ponderado'] = df[[f'{col}_score' for col in indicadores]].sum(axis=1)
    df['DY/mês'] = ((df['ÚLTIMO RENDIMENTO'] / df['Cotação'])* 100).round(2)
    df['YOC'] = ((df['Dividendos em 12 meses'] / df['Cotação']) * 100).round(2)
    
    # Ordenar
    df = df.drop(columns=['Vacância Média_score', 'P/VP_score', 'Dividend Yield_score', 'Liquidez_score'])
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    df.insert(0, 'Rank', range(1, len(df) + 1))
    df.rename(columns={'TIPO DE FUNDO': 'Tipo'}, inplace=True)
    df.rename(columns={'SEGMENTO': 'Setor'}, inplace=True)
    ordered_df = df[['Rank', 'Papel', 'Setor', 'Tipo', 'Cotação', 'DY', 'P/VP', 'Liquidez', 'Vacância', 'DY/mês' ,'YOC']]
    df = ordered_df
    
    return df
print(rank_fiis())
def update_data():
    get_df1()
    get_df2()
update_data()


# Função para importar FIIs do df1.csv


def import_fiis_from_csv():
    try:
        # Carrega o CSV
        df = pd.read_csv("./df1.csv")
        
        # Limpa todos os registros existentes
        Fiis.objects.all().delete()
        
        # Insere novos registros
        for papel in df['Papel'].unique():
            Fiis.objects.create(papel=papel)
        
        print(f"Importados {len(df['Papel'].unique())} FIIs com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao importar FIIs: {str(e)}")
        return False

#import_fiis_from_csv()