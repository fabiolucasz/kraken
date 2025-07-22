import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os


class FiiSpider(scrapy.Spider):
    name = "fii_spider"
    allowed_domains = ["investidor10.com.br"]

    liquidez_minima = 500_000
    pvp_minimo = 0.70

    @staticmethod
    def filter_df1():
        """Filtra o arquivo df1.csv para aplicar as regras de liquidez e P/VP"""
        df = pd.read_csv("./df1.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        # Filtra os papéis conforme liquidez mínima e P/VP
        df = df[df["Liquidez"] >= FiiSpider.liquidez_minima]
        df = df[df["P/VP"] >= FiiSpider.pvp_minimo]
        # Ordena pelo Dividend Yield
        df = df.sort_values(by="Dividend Yield", ascending=False)
        return df

    def start_requests(self):
        """Método para gerar as URLs dinamicamente para cada papel no df1.csv filtrado"""
        df_filtered = FiiSpider.filter_df1()
        for papel in df_filtered["Papel"]:
            url = f"https://investidor10.com.br/fiis/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            item = {}

            # Coleta os títulos
            nomes2 = response.css('div.desc span.d-flex::text').getall()
            titulos2 = [nome.strip() for nome in nomes2]

            nomes = response.css('div._card-header div span::text').getall()
            titulo_cotacao = nomes[0].strip().split(" ")[1]
            titulo_dy = nomes[1].strip().split(" ")[1]
            titulo_pvp = nomes[2].strip()
            titulo_liquidez = nomes[3].strip().split(" ")[0]
            titulo_liquidez_unidade = "Liquidez_unidade"
            titulo_variacao = nomes[4].strip().split(" ")[0]
            titulo_dy_pago_ult_12m = "DY_Pago_ult_12m"

            titulos = [titulo_cotacao, titulo_dy, titulo_pvp, titulo_liquidez, titulo_liquidez_unidade, titulo_variacao, titulo_dy_pago_ult_12m] + titulos2

            # Valores (caixas principais)
            valores_div = response.css('div._card-body div span::text').getall()
            cotacao = valores_div[0].strip().replace("R$ ", "").replace(",", ".")
            dy = valores_div[1].strip().replace("%", "").replace(",", ".")

            valores1_div = response.css('div._card-body span::text').getall()
            pvp = valores1_div[2].strip().replace("%", "").replace(",", ".")
            liquidez = valores1_div[3].strip().split(" ")[1].replace(",", ".")
            liquidez_unidade = valores1_div[3].strip().split(" ")[2]
            variacao = valores1_div[4].strip().replace("%", "").replace(",", ".")
            dy_ult_12m = response.css('div.dy-history h3.box-span::text').getall()
            dy_pago_ult_12m = dy_ult_12m[-1].strip().split(" ")[6].replace(",", ".")


            valores_div2 = response.css('div.value span::text').getall()
            valores2 = [valor.strip().replace(",", ".") for valor in valores_div2]

            valores = [cotacao, dy] + [pvp, liquidez, liquidez_unidade, variacao]+ [dy_pago_ult_12m] + valores2

            while len(valores) < len(titulos):
                valores.append("")

            dados = dict(zip(titulos, valores))
            dados["Papel"] = response.meta['papel']  # Adicionando o nome do papel

            yield dados

        except Exception as e:
            self.logger.error(f"Erro ao processar página: {e}")

    @staticmethod
    def process_df2():
        """Função para tratar e formatar os dados extraídos no df2_teste.csv"""
        df = pd.read_csv("./df2_teste.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

        colunas_percentuais = ["TAXA DE ADMINISTRAÇÃO", "VACÂNCIA"]
        colunas_valores = ["NUMERO DE COTISTAS", "COTAS EMITIDAS"]
        colunas_cotacao = ["VAL. PATRIMONIAL P/ COTA", "ÚLTIMO RENDIMENTO",]

        for col in colunas_percentuais:
            df[col] = df[col].astype(str).str.replace("%", "", regex=False).str.replace(",", ".")
            df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in colunas_valores:
            df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in colunas_cotacao:
            df[col] = df[col].astype(str).str.replace(r"\D", "", regex=True)  
            df[col] = df[col].apply(lambda x: float(x.zfill(3)[:-2] + "." + x.zfill(3)[-2:]) if x else None)

        df.to_csv('./final.csv', index=False)
        return df
    
    @staticmethod
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


# Rodando o Spider programaticamente
if __name__ == "__main__":
    # Apagar o arquivo antigo, caso exista
    if os.path.exists('./df2_teste.csv'):
        os.remove('./df2_teste.csv')

    # Configurar o processo do Scrapy
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'csv',
        'FEED_URI': './df2_teste.csv',  # Arquivo CSV onde os dados serão salvos
        'LOG_LEVEL': 'ERROR',  # Configuração de log para evitar logs excessivos
    })

    # Iniciar o Spider
    process.crawl(FiiSpider)
    process.start()

    # Após o Spider concluir, processa o df2_teste.csv
    FiiSpider.process_df2()
