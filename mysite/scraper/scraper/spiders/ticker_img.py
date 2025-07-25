import scrapy
import os
from scrapy.crawler import CrawlerProcess
import pandas as pd

class BaixarImagensSpider(scrapy.Spider):
    name = 'baixar_imagens'
    allowed_domains = ["investidor10.com.br"]

    def start_requests(self):
        df = pd.read_csv("acoes-listadas-b3.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df["Ticker"]:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})
        #Teste de um papel
        # ticker = "BBAS3"
        # url = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
        # yield scrapy.Request(url, callback=self.parse, meta={'papel': ticker})
    def parse(self, response):
        try:
            get_img = response.css('div.logo img::attr(src)').getall()
            img = get_img[2]
            ticker_img = response.urljoin(img)
            yield scrapy.Request(
                    url=ticker_img,
                    callback=self.salvar_imagem,
                meta={'nome_arquivo': f"{response.meta['papel']}.jpg"}
            )
        except Exception as e:
            self.logger.error(f"Erro ao processar página: {e}")

    def salvar_imagem(self, response):
        # Remove os números do nome do arquivo, mantendo apenas as letras
        nome_arquivo = ''.join(filter(str.isalpha, response.meta['nome_arquivo']))
        pasta = os.path.join('mysite', 'static', 'img', 'companies2')
        #pasta = os.path.join('mysite', 'static', 'img', 'companies')
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        with open(caminho, 'wb') as f:
            f.write(response.body)

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'LOG_LEVEL': 'INFO',  # para menos logs ou DEBUG para mais
    })
    
    # Inicia o Scrapy
    process.crawl(BaixarImagensSpider)
    process.start()
    
