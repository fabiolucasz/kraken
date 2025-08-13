import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd


class AcaoSpider(scrapy.Spider):
    name = "acao_spider"
    allowed_domains = ["investidor10.com.br"]

    dados_kpi = []
    dados_indicadores = []
    dados_info = []
    dados_img = []
    #dados_dpa = []

    def start_requests(self):
        df = pd.read_csv("acoes-listadas-b3.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df['Ticker']:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})
        # papel = "BBAS3"
        # url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
        # yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            papel = response.meta['papel']

            #Link da imagem
            img = response.css('div#container-ticker-data img::attr(src)').getall()
            img = img[0]
            ticker_img = response.urljoin(img)
            while len(ticker_img) < len(papel):
                ticker_img.append(" ")
            self.dados_img.append(dict(zip(["Papel", "Ticker_Img"], [papel, ticker_img])))

            # KPIs
            kpis = [k.strip().replace(" ", "_") for k in response.css('div._card-header div span::text').getall() if k.strip()]
            kpi_values = [v.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(",", ".") for v in response.css('div._card-body span::text').getall() if v.strip()]
            while len(kpi_values) < len(kpis):
                kpi_values.append("")
            self.dados_kpi.append(dict(zip(kpis, kpi_values), Papel=papel))

            # Indicadores
            indicadores = [i.strip().replace(" ", "_").replace(f"DIVIDEND_YIELD__-_{response.meta['papel']}", "DY") for i in response.css('div.cell span.d-flex::text').getall() if i.strip()]
            indicadores_values = [iv.strip().replace(",", ".").replace("%", "") for iv in response.css('div.value span::text').getall() if iv.strip()]
            while len(indicadores_values) < len(indicadores):
                indicadores_values.append("")
            self.dados_indicadores.append(dict(zip(indicadores, indicadores_values), Papel=papel))

            # Informações da ação
            info = [i.strip().replace(" ", "_").replace("Segmento_de_Listagem", "Liquidez_Média_Diária").replace("Free_Float", "Segmento_de_Listagem").replace("Tag_Along", "Free_Float").replace("Liquidez_Média_Diária", "Tag_Along") for i in response.css('div.cell span.title::text').getall() if i.strip()]
            info_values_div = [iv.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(".", "").replace(",", ".") for iv in response.css('span.value div.detail-value::text').getall() if iv.strip()]
            info_values_text = [iv.strip().replace(" ", "_").replace("%", "").replace("R$", "").replace(",", ".") for iv in response.css('div.cell span.value::text').getall() if iv.strip()]
            info_values = info_values_div + info_values_text
            while len(info_values) < len(info):
                info_values.append("")
            self.dados_info.append(dict(zip(info, info_values), Papel=papel))

            # # DPA
            # dpa = [d.strip().replace(" ", "_") for d in response.xpath('//*[@id="table-dividends-history_wrapper"]/div[1]/div[1]/div/table/thead/tr/th[1]/text()').getall() if d.strip()]
            # print(dpa)
            # dpa_values = [dv.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(".", "").replace(",", ".") for dv in response.xpath('//*[@id="table-dividends-history_wrapper"]/div[1]/div[1]/div/table/tbody/tr/td[1]/text()').getall() if dv.strip()]
            # print(dpa_values)
            # while len(dpa_values) < len(dpa):
            #     dpa_values.append("")
            # self.dados_dpa.append(dict(zip(dpa, dpa_values), Papel=papel))

            print(f"{papel} coletado com sucesso")

            df1 = pd.DataFrame(self.dados_kpi).fillna("")
            df2 = pd.DataFrame(self.dados_indicadores).fillna("")
            df3 = pd.DataFrame(self.dados_info).fillna("")
            df4 = pd.DataFrame(self.dados_img).fillna("")
            #df5 = pd.DataFrame(self.dados_dpa)
            df = pd.merge(df1, df2).merge(df3).merge(df4)
            df['P/L'] = df['P/L'].apply(remover_segundo_ponto)
            df['PAYOUT'] = df['PAYOUT'].apply(remover_segundo_ponto)
            df['ROE'] = df['ROE'].apply(remover_segundo_ponto)
            df = df.drop(columns=["carteira_investidor_10"])
            df = df.applymap(lambda x: "" if x == "-" else x)
            df.to_csv("acoes.csv", index=False, encoding='utf-8')
            
            
        except Exception as e:
            self.logger.error(f"Erro ao processar {papel}: {e}")

def run_scraper():
    process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR'})
    process.crawl(AcaoSpider)
    process.start()
    print("Todos os dados foram salvos com sucesso!")




def remover_segundo_ponto(val):
    if pd.isna(val):
        return val
    val = str(val).strip()
    val = val.replace(',', '.')        
    partes = val.split('.')           
    if len(partes) > 2:
        return '.'.join(partes[:-1]) + partes[-1]
    return val

run_scraper()


