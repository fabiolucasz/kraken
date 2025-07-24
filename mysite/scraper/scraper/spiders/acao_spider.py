import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import time
import os

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class AcaoSpider(scrapy.Spider):
    name = "acao_spider"
    allowed_domains = ["investidor10.com.br"]

    def start_requests(self):
        df = pd.read_csv("acoes-listadas-b3.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df["Ticker"]:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            item = {}

            nomes = response.css('div._card-header div span::text').getall()
            titulo_cotacao = nomes[0].strip()
            titulo_variacao = nomes[1].strip().split(" ")[0]
            titulo_pl = nomes[2].strip()
            titulo_pvp = nomes[3].strip()
            titulo_dy = nomes[4].strip()

            nomes2 = response.css('div.cell span.d-flex::text').getall()
            titulos2 = [nome.strip() for nome in nomes2]

            titulos = [titulo_cotacao, titulo_variacao, titulo_pl, titulo_pvp, titulo_dy] + titulos2

            # Valores (caixas principais)
            valores_div = response.css('div._card-body div span::text').getall()
            cotacao = valores_div[0].strip().replace("R$ ", "").replace(",", ".")
            variacao = valores_div[1].strip().replace("%", "").replace(",", ".")

            valores1_div = response.css('div._card-body span::text').getall()
            pl = valores1_div[2].strip().replace(",", ".")
            pvp = valores1_div[3].strip().replace(",", ".")
            dy = valores1_div[4].strip().replace(",", ".").replace("%", "")


            valores_div2 = response.css('div.value span::text').getall()
            valores2 = [valor.strip().replace(",", ".").replace("%", "") for valor in valores_div2]

            valores = [cotacao, variacao] + [pl, pvp, dy] + valores2

            while len(valores) < len(titulos):
                valores.append("")

            dados = dict(zip(titulos, valores))
            dados["Papel"] = response.meta['papel']  # Adicionando o nome do papel

            yield dados

        except Exception as e:
            self.logger.error(f"Erro ao processar página: {e}")

    @staticmethod
    def process_acoes(file_path):
        df = pd.read_csv(file_path, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        df.to_csv('acoes.csv', index=False)
        return df

if __name__ == "__main__":
    # Criar um nome único para o arquivo temporário baseado no timestamp
    
    timestamp = int(time.time())
    temp_file = f'acoes_temp_{timestamp}.csv'
    # Configurar o processo do Scrapy
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'csv',
        'FEED_URI': temp_file,  # Arquivo temporário onde os dados serão salvos
        'LOG_LEVEL': 'ERROR',  # Configuração de log para evitar logs excessivos
    })


    # Iniciar o Spider
    process.crawl(AcaoSpider)
    process.start()

    # Após o Spider concluir, processa o arquivo temporário e salva o resultado final
    df = AcaoSpider.process_acoes(temp_file)
    # Remove o arquivo temporário
    os.remove(temp_file)