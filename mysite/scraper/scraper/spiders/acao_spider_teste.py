import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

#Pegar a porra das tabelas e gráficos.

class AcaoSpider(scrapy.Spider):
    name = "acao_spider"
    allowed_domains = ["investidor10.com.br"]

    def start_requests(self):
        df = pd.read_csv("acoes.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df['Papel']:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

        # Teste de um papel
        # papel = "BBAS3"
        # url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
        # yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            item = {}

            # kpis principais
            get_kpi = response.css('div._card-header div span::text').getall()
            kpis = [k.strip().replace(" ", "_").replace('carteira_investidor_10', '') for k in get_kpi if k.strip()]

            # valor kpis
            get_kpi_value = response.css('div._card-body span::text').getall()
            kpi_value = [v.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(",", ".") for v in get_kpi_value if v.strip()]

            while len(kpi_value) < len(kpis):
                 kpi_value.append("")

            dados_kpi = dict(zip(kpis, kpi_value))
            dados_kpi["Papel"] = response.meta['papel']

            # indicadores fundamentalistas
            get_indicadores = response.css('div.cell span.d-flex::text').getall()
            indicadores = [i.strip().replace(" ", "_").replace(f"DIVIDEND_YIELD__-_{response.meta['papel']}", "Dividend_Yield") for i in get_indicadores if i.strip()]

            # valor indicadores fundamentalistas
            get_indicadores_value = response.css('div.value span::text').getall()
            indicadores_value = [iv.strip().replace(",", ".").replace("%", "") for iv in get_indicadores_value if iv.strip()]


            while len(indicadores_value) < len(indicadores):
                 indicadores_value.append("")

            dados_indicadores = dict(zip(indicadores, indicadores_value))
            dados_indicadores["Papel"] = response.meta['papel']


            #historico de indicadores fundamentalistas
            #get_indicadores_historico = response.css('table th::text').getall()
            #indicadores_historico = [iv.strip().replace(",", ".").replace("%", "") for iv in get_indicadores_historico]
            #print(indicadores_historico)

            #informações da ação
            get_info = response.css('div.cell  span.title::text').getall()
            info = [i.strip().replace(" ", "_").replace("Segmento_de_Listagem", "Liquidez_Média_Diária").replace("Free_Float", "Segmento_de_Listagem").replace("Tag_Along", "Free_Float").replace("Liquidez_Média_Diária", "Tag_Along") for i in get_info if i.strip()]

            # dados das informações da ação
            get_info_value = response.css('span.value div.detail-value::text').getall()
            info_value = [iv.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(",", ".").replace(".","") for iv in get_info_value if iv.strip()]
            get_info_value_text = response.css('div.cell span.value::text').getall()
            info_value_text = [iv.strip().replace(" ", "_").replace("%", "").replace("R$", "").replace(",", ".") for iv in get_info_value_text if iv.strip()]
            info_values = info_value + info_value_text

            while len(info_values) < len(info):
                info_values.append("")

            dados_info = dict(zip(info, info_values))
            dados_info["Papel"] = response.meta['papel'] 
            
           

            pd.DataFrame([dados_kpi]).to_csv(f"./data_csv/{response.meta['papel']}_kpi.csv", index=False)
            pd.DataFrame([dados_indicadores]).to_csv(f"./data_csv/{response.meta['papel']}_indicadores.csv", index=False)
            pd.DataFrame([dados_info]).to_csv(f"./data_csv/{response.meta['papel']}_info.csv", index=False)

        except Exception as e:
            self.logger.error(f"Erro ao processar página {response.meta['papel']}: {e}")


if __name__ == "__main__":

    # Remover arquivo anterior se desejar sobrescrever
    # if os.path.exists(output_file):
    #     os.remove(output_file)

    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'ERROR',
    })

    process.crawl(AcaoSpider)
    process.start()

    print(f"Dados salvos com sucesso!")
