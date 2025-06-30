from django.shortcuts import render
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from sklearn.preprocessing import MinMaxScaler
import asyncio
import aiohttp
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
    df.to_csv('../df1.csv', index=False)
    df = process_df1()
    df.to_csv('../df1.csv', index=False)
    return df

def filter_df1(liquidez_minima, pvp):
    df = pd.read_csv("../df1.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    df = df[df["Liquidez"] >= liquidez_minima]
    df = df[df["P/VP"] >= pvp]
    df = df.sort_values(by="Dividend Yield", ascending=False)
    return df


def process_df1():
    df = pd.read_csv("../df1.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    
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
    df.to_csv('../df1.csv', index=False)
    
    return df

def get_df2():
    fiis = filter_df1(liquidez_minima, pvp_minimo)
    tickers = fiis["Papel"].tolist()
    all_fiis = []

    for papel in tickers:
        print(f"✔️ {papel}")
        try:
            url = f"https://investidor10.com.br/fiis/{papel}/"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            titulo1 = [item.text.strip() for item in soup.find_all('span', class_="name")]
            titulo2 = ["Dividendos em 12 meses"]
            titulos = [titulo1,titulo2]
            titulos = [item for sublist in titulos for item in sublist]
            valor1 = [item.text.strip() for item in soup.find_all('div', class_="value")]
            dividendo_div = soup.find_all('h3', class_="box-span" )
            ultimo_valor = dividendo_div[-1].text.strip().split(" ")[6].replace(",",".")
            valor2 = [ultimo_valor]
            valores = [valor1,valor2]
            valores = [item for sublist in valores for item in sublist]

            dados_fiis = dict(zip(titulos, valores))
            dados_fiis["Papel"] = papel
            all_fiis.append(dados_fiis)
        except Exception as e:
            print(f"❌ Erro ao processar {papel}: {e}")
            return {"Papel": papel}
    
    df = pd.DataFrame(all_fiis)
    df.to_csv("df2.csv", index=False)
    #df = tratar_df2()
    df.to_csv("df2.csv", index=False)
    merge()
    return df
async def fetch(session, papel, headers):
    url = f"https://investidor10.com.br/fiis/{papel}/"
    try:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            titulo1 = [item.text.strip() for item in soup.find_all('span', class_="name")]
            titulo2 = ["Dividendos em 12 meses"]
            titulos = [titulo1,titulo2]
            titulos = [item for sublist in titulos for item in sublist]
            valor1 = [item.text.strip() for item in soup.find_all('div', class_="value")]
            dividendo_div = soup.find_all('h3', class_="box-span" )
            ultimo_valor = dividendo_div[-1].text.strip().split(" ")[6].replace(",",".")
            valor2 = [ultimo_valor]
            valores = [valor1,valor2]
            valores = [item for sublist in valores for item in sublist]

            dados_fiis = dict(zip(titulos, valores))
            dados_fiis["Papel"] = papel
            print(f"✔️ {papel}")
            return dados_fiis
    except Exception as e:
        print(f"❌ Erro ao processar {papel}: {e}")
        return {"Papel": papel}

async def get_data_com_async():
    fiis = filter_df1(liquidez_minima, pvp_minimo)
    tickers = fiis["Papel"].tolist()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for papel in tickers:
            tasks.append(fetch(session, papel, headers))
        todos_os_fiis = await asyncio.gather(*tasks)

    df = pd.DataFrame(todos_os_fiis)
    df.to_csv("../df2.csv", index=False)
    #df = tratar_df2()
    df.to_csv("../df2.csv", index=False)
    merge()
    return df

def get_data_com():
    return asyncio.run(get_data_com_async())

def merge():
    df1 = filter_df1(liquidez_minima, pvp_minimo)
    df2 = pd.read_csv("../df2.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    merge = pd.merge(df1, df2, on="Papel", how="inner")
    merge.to_csv("../merge.csv", index=False)
    #merge = pd.read_csv("../merge.csv")
    #ordem = ["Papel", "Segmento", "TIPO DE FUNDO", "VAL. PATRIMONIAL P/ COTA", "Cotação", "Dividend Yield", "P/VP", "ÚLTIMO RENDIMENTO", "FFO Yield", "Liquidez", "Valor de Mercado", "Qtd de imóveis", "Cap Rate", "Vacância Média", "VALOR PATRIMONIAL"]
    #merge = merge[ordem]
    #merge.to_csv("../merge.csv", index=False)
    return merge

def process_data():
    df = pd.read_csv("../merge.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    df = df.drop(columns=["Preço do m2", "Aluguel por m2", "Qtd de imóveis", "Cap Rate"], errors="ignore")

    colunas_percentuais = ["FFO Yield", "Dividend Yield", "Vacância Média"]
    colunas_valores = ["Valor de Mercado", "Liquidez"]
    colunas_cotacao = ["Cotação"]
    colunas_pvp = ["P/VP"]

    for col in colunas_percentuais:
        df[col] = df[col].astype(str).str.replace("%", "", regex=False).str.replace(",", ".")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in colunas_valores:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce")

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
    return df





def rank_fiis(df):
    df = df.copy()
    
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
    
    # Ordenar
    df = df.drop(columns=['Vacância Média_score', 'P/VP_score', 'Dividend Yield_score', 'Liquidez_score'])
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    df.insert(0, 'Rank', range(1, len(df) + 1))
    ordered_df = df[['Favoritos', 'Rank', 'Papel', 'Segmento', 'Cotação', 'Dividend Yield', 'P/VP', 'Liquidez', 'Vacância Média']]
    df = ordered_df

    return df
def index(request):
    df = process_data()
    
    # Aplicando filtros baseados nos parâmetros da URL
    filters = {}
    
    # Dividend Yield
    if 'dividend_yield_min' in request.GET:
        try:
            min_yield = float(request.GET['dividend_yield_min'])
            df = df[df['Dividend Yield'] >= min_yield]
            filters['dividend_yield_min'] = min_yield
        except ValueError:
            pass
    
    # Liquidez
    if 'liquidez_min' in request.GET:
        try:
            min_liquidez = float(request.GET['liquidez_min'])
            df = df[df['Liquidez'] >= min_liquidez]
            filters['liquidez_min'] = min_liquidez
        except ValueError:
            pass
    
    # Vacância
    if 'vacancia_max' in request.GET:
        try:
            max_vacancia = float(request.GET['vacancia_max'])
            df = df[df['Vacância Média'] <= max_vacancia]
            filters['vacancia_max'] = max_vacancia
        except ValueError:
            pass
    
    # PVP
    if 'pvp_min' in request.GET:
        try:
            min_pvp = float(request.GET['pvp_min'])
            df = df[df['P/VP'] >= min_pvp]
            filters['pvp_min'] = min_pvp
        except ValueError:
            pass
    
    if 'pvp_max' in request.GET:
        try:
            max_pvp = float(request.GET['pvp_max'])
            df = df[df['P/VP'] <= max_pvp]
            filters['pvp_max'] = max_pvp
        except ValueError:
            pass
    
    # Segmento
    if 'segmento' in request.GET:
        segmento = request.GET['segmento'].strip()
        if segmento:
            df = df[df['Segmento'].str.contains(segmento, case=False, na=False)]
            filters['segmento'] = segmento

    df= rank_fiis(df)

    data = df.to_dict('records')
    columns = df.columns.tolist()
    
    return render(request, 'fiis/index.html', {
        'data': data, 
        'columns': columns,
        'filters': filters
    })

def update_data():
    get_df1()
    print(filter_df1(liquidez_minima, pvp_minimo))
    #get_df2()
    get_data_com()

update_data()
