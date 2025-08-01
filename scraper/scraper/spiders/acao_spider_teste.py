import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os

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



if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'ERROR',
    })

    process.crawl(AcaoSpider)
    process.start()

    merge_acoes()

    print(f"Dados salvos com sucesso!")
