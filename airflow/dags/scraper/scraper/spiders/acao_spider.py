import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os


class AcaoSpider(scrapy.Spider):
    name = "acao_spider"
    allowed_domains = ["investidor10.com.br"]

    dados_kpi = []
    dados_indicadores = []
    dados_info = []
    dados_img = []

    def start_requests(self):
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Read the input file from data directory
        input_path = os.path.join(data_dir, 'acoes-listadas-b3.csv')
        df = pd.read_csv(input_path, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df['Ticker']:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            papel = response.meta['papel']
            print(f"Processando: {papel}")

            #Link da imagem
            img = response.css('div#container-ticker-data img::attr(src)').getall()
            img = img[0]
            ticker_img = response.urljoin(img)
            while len(ticker_img) < len(papel):
                ticker_img.append(" ")
            self.dados_img.append(dict(zip(["Papel", "Ticker_Img"], [papel, ticker_img])))

            df_img = pd.DataFrame(self.dados_img).fillna("")
            df_img.columns = df_img.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            df_img = df_img.applymap(lambda x: str(x).lower().strip().replace('-', '') if isinstance(x, str) else x)
            df_img.to_csv(os.path.join(data_dir, "acoes_img.csv"), index=False)

            # KPIs
            kpis = [k.strip().replace(" ", "_") for k in response.css('div._card-header div span::text').getall() if k.strip()]
            kpi_values = [v.strip().replace(" ", "").replace("%", "").replace("R$", "").replace('.','').replace(",", ".") for v in response.css('div._card-body span::text').getall() if v.strip()]
            while len(kpi_values) < len(kpis):
                kpi_values.append("")
            self.dados_kpi.append(dict(zip(kpis, kpi_values), Papel=papel))

            df_kpi = pd.DataFrame(self.dados_kpi).fillna("")
            df_kpi.columns = df_kpi.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            df_kpi = df_kpi.applymap(lambda x: str(x).lower().strip().replace('-', '').replace('_', ' ') if isinstance(x, str) else x)
            df_kpi.to_csv(os.path.join(data_dir, "acoes_kpi.csv"), index=False)

            # Indicadores
            indicadores = [i.strip().replace(" ", "_").replace(f"DIVIDEND_YIELD__-_{response.meta['papel']}", "DY").replace('.', '') for i in response.css('div.cell span.d-flex::text').getall() if i.strip()]
            indicadores_values = [iv.strip().replace(".", "").replace(",", ".").replace("%", "") for iv in response.css('div.value span::text').getall() if iv.strip()]
            while len(indicadores_values) < len(indicadores):
                indicadores_values.append("")
            self.dados_indicadores.append(dict(zip(indicadores, indicadores_values), Papel=papel))

            df_indicadores = pd.DataFrame(self.dados_indicadores).fillna("")
            df_indicadores.columns = df_indicadores.columns.str.lower().str.strip().str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            df_indicadores = df_indicadores.applymap(lambda x: str(x).lower().strip().replace('-', '').replace('_', ' ') if isinstance(x, str) else x)
            df_indicadores.to_csv(os.path.join(data_dir, "acoes_indicadores.csv"), index=False)

            # Informações da ação
            info = [i.strip().replace(" ", "_").replace("Segmento_de_Listagem", "Liquidez_Média_Diária").replace("Free_Float", "Segmento_de_Listagem").replace("Tag_Along", "Free_Float").replace("Liquidez_Média_Diária", "Tag_Along") for i in response.css('div.cell span.title::text').getall() if i.strip()]
            info_values_div = [iv.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(".", "").replace(",", ".") for iv in response.css('span.value div.detail-value::text').getall() if iv.strip()]
            info_values_text = [iv.strip().replace(" ", "_").replace("%", "").replace("R$", "").replace(",", ".") for iv in response.css('div.cell span.value::text').getall() if iv.strip()]
            info_values = info_values_div + info_values_text
            while len(info_values) < len(info):
                info_values.append("")
            self.dados_info.append(dict(zip(info, info_values), Papel=papel))

            df_info = pd.DataFrame(self.dados_info).fillna("")
            df_info.columns = df_info.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('º', '').str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            df_info = df_info.applymap(lambda x: str(x).lower().strip().replace('-', '').replace('_', ' ').replace('_', ' ') if isinstance(x, str) else x)
            df_info.to_csv(os.path.join(data_dir, "acoes_info.csv"), index=False)

        except Exception as e:
            self.logger.error(f"Erro ao processar {papel}: {e}")

def remover_segundo_ponto(val):
    if pd.isna(val):
        return val
    val = str(val).strip()
    val = val.replace(',', '.')        
    partes = val.split('.')           
    if len(partes) > 2:
        return '.'.join(partes[:-1]) + partes[-1]
    return val

def run_scraper():

    process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR'})
    spider = AcaoSpider()
    process.crawl(AcaoSpider)
    process.start()

    print("\nProcesso de coleta de dados finalizado.")
    

if __name__ == "__main__":
    run_scraper()