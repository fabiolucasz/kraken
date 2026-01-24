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
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        data_dir = os.path.join(base_dir, 'include', 'data')
        print(f"data_dir start_requests: {data_dir}")
        #os.makedirs(data_dir, exist_ok=True)
        
        # Read the input file from data directory
        input_path = os.path.join(data_dir, 'acoes-listadas-b3.csv')
        df = pd.read_csv(input_path, quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        print(f"Total de Ações para coletar: {len(df['Ticker'])}")
        #limitar para testes
        #df = df.head(10)
        for papel in df['Ticker']:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    async def parse(self, response):    
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            data_dir = os.path.join(base_dir, 'include', 'dbt_dw', 'kraken_dw', 'seeds')
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
            #df_img = df_img.applymap(lambda x: str(x).lower().strip().replace('-', '') if isinstance(x, str) else x)
            df_img.to_csv(os.path.join(data_dir, "acoes_img.csv"), index=False)

            # KPIs
            kpis = [k.strip().replace(" ", "_") for k in response.css('div._card-header div span::text').getall() if k.strip()]
            kpi_values = [v.strip().replace(" ", "").replace("%", "").replace("R$", "").replace('.','').replace(",", ".") for v in response.css('div._card-body span::text').getall() if v.strip()]
            while len(kpi_values) < len(kpis):
                kpi_values.append("")
            self.dados_kpi.append(dict(zip(kpis, kpi_values), Papel=papel))

            df_kpi = pd.DataFrame(self.dados_kpi).fillna("")
            df_kpi.columns = df_kpi.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            #df_kpi = df_kpi.applymap(lambda x: str(x).lower().strip().replace('-', '').replace('_', ' ') if isinstance(x, str) else x)
            df_kpi = df_kpi.drop(columns=["carteira_investidor_10"])
            df_kpi.to_csv(os.path.join(data_dir, "acoes_kpi.csv"), index=False)

            # Indicadores
            indicadores = [i.strip().replace(" ", "_").replace(f"DIVIDEND_YIELD__-_{response.meta['papel']}", "DY").replace('.', '') for i in response.css('div.cell span.d-flex::text').getall() if i.strip()]
            indicadores_values = [iv.strip().replace(".", "").replace(",", ".").replace("%", "") for iv in response.css('div.value span::text').getall() if iv.strip()]
            while len(indicadores_values) < len(indicadores):
                indicadores_values.append("")
            self.dados_indicadores.append(dict(zip(indicadores, indicadores_values), Papel=papel))

            df_indicadores = pd.DataFrame(self.dados_indicadores).fillna("")
            df_indicadores.columns = df_indicadores.columns.str.lower().str.strip().str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
            #df_indicadores = df_indicadores.applymap(lambda x: str(x).lower().strip().replace('-', '').replace('_', ' ') if isinstance(x, str) else x)
            df_indicadores.to_csv(os.path.join(data_dir, "acoes_indicadores.csv"), index=False)

            # Informações da ação
            def extract_info_value(response, index):
                """
                Extrai o valor de uma célula da tabela Informações da Ação.
                """
                # Tenta encontrar o detail-value primeiro
                detail_selector = f'div.cell:nth-child({index + 1}) span.value div.detail-value::text'
                value = response.css(detail_selector).get()
                
                # Se não encontrar, tenta o simple-value
                if not value:
                    simple_selector = f'div.cell:nth-child({index + 1}) span.value div.simple-value::text'
                    value = response.css(simple_selector).get()
                
                # Se ainda não encontrou, tenta o span.value direto
                if not value:
                    value_selector = f'div.cell:nth-child({index + 1}) span.value::text'
                    value = response.css(value_selector).get()
                
                return value.strip().replace('R$ ', '').replace('%','').replace(',', '.') if value else ""

            
            detail_titles = [dt.strip() for dt in response.css('div.cell span.title::text').getall() if dt.strip()]
            detail_values = []

            # Para cada título, tenta extrair o valor correspondente
            for i in range(len(detail_titles)):
                value = extract_info_value(response, i)
                detail_values.append(value)

            # Agora cria o dicionário com os valores extraídos
            if detail_titles and detail_values:
                self.dados_info.append(dict(zip(detail_titles, detail_values), Papel=papel))
                
                # Transformando e salvando
                df_info = pd.DataFrame(self.dados_info)
                df_info.columns = df_info.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('º', '').str.replace('-', '').str.replace('/','_').str.replace('(','').str.replace(')','')
                df_info = df_info.replace('-','')
                df_info.to_csv(os.path.join(data_dir, "acoes_info.csv"), index=False)
                df_info.to_json(os.path.join(data_dir, "acoes_info.json"), orient='records', indent=2, force_ascii=False)
                print(f"Processado: {papel}")

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