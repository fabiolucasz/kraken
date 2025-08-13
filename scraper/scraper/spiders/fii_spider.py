import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import time
import os

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class FiiSpider(scrapy.Spider):
    name = "fii_spider"
    allowed_domains = ["investidor10.com.br"]

    def start_requests(self):
        df_filtered = pd.read_csv("fiis-listados-b3-tratado.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df_filtered["Papel"]:
            url = f"https://investidor10.com.br/fiis/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            item = {}

            nomes = response.css('div._card-header div span::text').getall()
            titulo_cotacao = nomes[0].strip().split(" ")[1]
            titulo_dy = nomes[1].strip().split(" ")[1]
            titulo_pvp = nomes[2].strip()
            titulo_liquidez = nomes[3].strip().split(" ")[0]
            titulo_liquidez_unidade = "Liquidez_unidade"
            titulo_variacao = nomes[4].strip().split(" ")[0]
            titulo_dy_pago_ult_12m = "DY_Pago_ult_12m"

            nomes2 = response.css('div.desc span.d-flex::text').getall()
            titulos2 = [nome.strip() for nome in nomes2]

            titulos = [titulo_cotacao, titulo_dy, titulo_pvp, titulo_liquidez, titulo_liquidez_unidade, titulo_variacao, titulo_dy_pago_ult_12m] + titulos2


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
            self.logger.error(f"Erro ao processar {response.meta['papel']}: {e}")

    @staticmethod
    def process_df2(file_path):
        df = pd.read_csv(file_path, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

        colunas_percentuais = ["TAXA DE ADMINISTRAÇÃO", "VACÂNCIA", "DY", "DY_Pago_ult_12m", "Liquidez"]
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

        df.rename(columns={
            "SEGMENTO": "Setor",
            "TIPO DE FUNDO": "Tipo",
        }, inplace=True)

        return df

def run_fii():
    timestamp = int(time.time())
    temp_file = f'df2_temp_{timestamp}.csv'
    # Configurar o processo do Scrapy
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'csv',
        'FEED_URI': temp_file,  # Arquivo temporário onde os dados serão salvos
        'LOG_LEVEL': 'ERROR',  # Configuração de log para evitar logs excessivos
    })
    # Iniciar o Spider
    process.crawl(FiiSpider)
    process.start()

    # Após o Spider concluir, processa o arquivo temporário e salva o resultado final
    df = FiiSpider.process_df2(temp_file)
    df.to_csv('fiis.csv', index=False)
    # Remove o arquivo temporário
    os.remove(temp_file)

    return df

run_fii()
