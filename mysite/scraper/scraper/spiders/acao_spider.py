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
        #Teste de um papel
        # ticker = "BBAS3"
        # url = f"https://investidor10.com.br/acoes/{ticker.lower()}/"
        # yield scrapy.Request(url, callback=self.parse, meta={'papel': ticker})

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
            titulo_pl2 = nomes2[0].strip()
            titulo_psr = nomes2[1].strip().split(" ")[0]
            titulo_pvp2 = nomes2[2].strip().split(" ")[0]
            titulo_dy2 = nomes2[3].strip().split(" ")[0].replace("DIVIDEND", "DY")


            titulo_payout = nomes2[4].strip()
            titulo_margem_liquida = nomes2[5].strip().replace(" ", "_")
            titulo_margem_bruta = nomes2[6].strip().replace(" ", "_")
            titulo_margem_ebit = nomes2[7].strip().replace(" ", "_")


            titulo_margem_ebitda = nomes2[8].strip().replace(" ", "_")


            titulo_ev_ebit = nomes2[9].strip()
            titulo_p_ebit = nomes2[10].strip()
            titulo_p_ativo = nomes2[11].strip()
            titulo_p_cap_giro = nomes2[12].strip()


            titulo_p_ativo_circ_liq = nomes2[13].strip().replace(" ", "_")
            titulo_vpa = nomes2[14].strip()
            titulo_lpa = nomes2[15].strip()
            titulo_giro_ativos = nomes2[16].strip().replace(" ", "_")


            titulo_roe = nomes2[17].strip()
            titulo_roic = nomes2[18].strip()
            titulo_roa = nomes2[19].strip()
            titulo_patrimonio_ativos = nomes2[20].strip().replace(" ", "")


            titulo_passivos_ativos = nomes2[21].strip().replace(" ", "")
            titulo_liquidez_corrente = nomes2[22].strip().replace(" ", "_")
            titulo_cagr_receitas_5_anos = nomes2[23].strip().replace(" ", "_")
            titulo_cagr_lucros_5_anos = nomes2[24].strip().replace(" ", "_")

            titulos = [titulo_cotacao, titulo_variacao, titulo_pl, titulo_pvp, titulo_dy] + [titulo_pl2, titulo_psr, titulo_pvp2, titulo_dy2, titulo_payout, titulo_margem_liquida, titulo_margem_bruta, titulo_margem_ebit, titulo_margem_ebitda, titulo_ev_ebit, titulo_p_ebit, titulo_p_ativo, titulo_p_cap_giro, titulo_p_ativo_circ_liq, titulo_vpa, titulo_lpa, titulo_giro_ativos, titulo_roe, titulo_roic, titulo_roa, titulo_patrimonio_ativos, titulo_passivos_ativos, titulo_liquidez_corrente, titulo_cagr_receitas_5_anos, titulo_cagr_lucros_5_anos]

            # Valores (caixas principais)
            valores_div = response.css('div._card-body div span::text').getall()
            cotacao = valores_div[0].strip().replace("R$ ", "").replace(",", ".")
            variacao = valores_div[1].strip().replace("%", "").replace(",", ".")

            valores1_div = response.css('div._card-body span::text').getall()
            pl = valores1_div[2].strip().replace(".","").replace(",", ".")
            pvp = valores1_div[3].strip().replace(".","").replace(",", ".")
            dy = valores1_div[4].strip().replace(".","").replace(",", ".").replace("%", "")


            valores_div2 = response.css('div.value span::text').getall()
            valores2 = [valor.strip().replace(".","").replace(",", ".").replace("%", "") for valor in valores_div2]

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