import requests
from bs4 import BeautifulSoup
from io import StringIO
from sklearn.preprocessing import MinMaxScaler
import asyncio
import aiohttp
import pandas as pd

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
    df.to_csv('./df1_teste.csv', index=False)
    df = process_df1()
    df.to_csv('./df1_teste.csv', index=False)
    return df

def process_df1():
    df = pd.read_csv("./df1_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
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
    df.to_csv('./df1_teste.csv', index=False)
    
    return df

def filter_df1(liquidez_minima, pvp):
    df = pd.read_csv("./df1_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    df = df[df["Liquidez"] >= liquidez_minima]
    df = df[df["P/VP"] >= pvp]
    df = df.sort_values(by="Dividend Yield", ascending=False)
    return df

def get_df2():
    papel = "mxrf11"
    url = f"https://investidor10.com.br/fiis/{papel.lower()}/"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo1 = [item.text.strip() for item in soup.find_all('span', class_="name")]
        titulo2 = ["Dividendos em 12 meses"]
        titulo3 = ["Cotação"]
        titulo4 = ["DY"]
        titulo5 = ["P/VP"]
        titulo6 = ["Liquidez"]
        titulo7 = ["Variação"]

        titulos = [titulo1, titulo2, titulo3, titulo4, titulo5, titulo6, titulo7]
        titulos = [item for sublist in titulos for item in sublist]

        valor1 = [item.text.strip() for item in soup.find_all('div', class_="value")]
        dividendo_div = soup.find_all('h3', class_="box-span")
        ultimo_valor = dividendo_div[-1].text.strip().split(" ")[6].replace(",", ".")
        valor2 = [ultimo_valor]
        valor3 = [item.text.strip() for item in soup.find_all('span', class_="value")]

        # extrair apenas texto dos primeiros spans encontrados
        div_span = soup.find_all('span')
        valor4 = div_span[23].text.strip()
        valor5 = div_span[24].text.strip()
        valor6 = div_span[25].text.strip()
        valor7 = div_span[26].text.strip()

        valores = valor1 + valor2 + valor3 + [valor4, valor5, valor6, valor7]

        dados_fii = dict(zip(titulos, valores))
        dados_fii["Papel"] = papel.upper()

        df = pd.DataFrame([dados_fii])
        df.to_csv(f"./teste_{papel.upper()}.csv", index=False)
        print(f"✔️ Dados salvos em teste_{papel.upper()}.csv")
        return df
    except Exception as e:
        print(f"❌ Erro ao buscar dados para {papel}: {e}")
        return pd.DataFrame()


def merge():
    df1 = filter_df1(liquidez_minima, pvp_minimo)
    df2 = pd.read_csv("./df2_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    merge = pd.merge(df1, df2, on="Papel", how="inner")
    merge.to_csv("./merge_teste.csv", index=False)
    merge = process_merged_df()
    merge.to_csv("./merge_teste.csv", index=False)
    return merge

def process_merged_df():
    df = pd.read_csv("./merge_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

    colunas_percentuais = ["TAXA DE ADMINISTRAÇÃO", "VACÂNCIA"]
    colunas_valores = ["NUMERO DE COTISTAS", "COTAS EMITIDAS"]
    colunas_cotacao = ["VAL. PATRIMONIAL P/ COTA", "ÚLTIMO RENDIMENTO", "Dividendos em 12 meses"]

    for col in colunas_percentuais:
        df[col] = df[col].astype(str).str.replace("%", "", regex=False).str.replace(",", ".")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in colunas_valores:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in colunas_cotacao:
        df[col] = df[col].astype(str).str.replace(r"\D", "", regex=True)  
        df[col] = df[col].apply(lambda x: float(x.zfill(3)[:-2] + "." + x.zfill(3)[-2:]) if x else None)

    df.to_csv('./merge_teste.csv', index=False)
    return df


def rank_fiis():
    df = pd.read_csv("./merge_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    
    # Indicadores relevantes
    indicadores = {
        'Dividend Yield': 1,  # quanto maior, melhor
        'Liquidez': 0.5,      # quanto maior, melhor
        'Vacância Média': -1, # quanto menor, melhor
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
    df.rename(columns={'Vacância Média': 'Vacância'}, inplace=True)
    df.rename(columns={'Dividend Yield': 'DY'}, inplace=True)
    df.rename(columns={'TIPO DE FUNDO': 'Tipo'}, inplace=True)
    df.rename(columns={'SEGMENTO': 'Setor'}, inplace=True)
    ordered_df = df[['Rank', 'Papel', 'Setor', 'Tipo', 'Cotação', 'DY', 'P/VP', 'Liquidez', 'Vacância', 'DY/mês' ,'YOC']]
    df = ordered_df
    
    return df

def update_data():
    get_df1()
    get_df2()
update_data()


