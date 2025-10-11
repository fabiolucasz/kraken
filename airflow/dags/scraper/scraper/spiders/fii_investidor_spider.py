import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os

class FiiSpider(scrapy.Spider):
    name = "fii_kpi_spider"
    allowed_domains = ["investidor10.com.br"]
    dados_kpi = []
    dados_info = []

    def start_requests(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        # df = pd.read_csv(os.path.join(data_dir,"fiis-listados-b3-tratado.csv"), quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        # fiis_list = df["Papel"].tolist()
        
        # For testing with just one FII
        fiis_list = ["MXRF11"]
        
        for papel in fiis_list:
            url = f"https://investidor10.com.br/fiis/{papel.lower().strip()}/"
            self.logger.info(f"Requisitando dados para {papel}...")
        
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})


    def parse(self, response):
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            papel = response.meta['papel']


            #Grid data
            titulos_kpi = response.xpath('//div[@class="_card-header"]//div//span/text()').getall()
            
            titulo_cotacao = titulos_kpi[0].strip().split(" ")[1]
            titulo_dy = titulos_kpi[1].strip().split(" ")[1]
            titulo_pvp = titulos_kpi[2].strip()
            titulo_liquidez = titulos_kpi[3].strip()
            titulo_liquidez_unidade = "Liquidez Unidade"
            titulo_variacao = titulos_kpi[4].strip().split(" ")[0]
            titulo_papel = "Papel"
            titulo_kpi = [titulo_cotacao, titulo_dy, titulo_pvp, titulo_liquidez, titulo_liquidez_unidade, titulo_variacao, titulo_papel]


            valores_kpi = response.xpath('//div[@class="_card-body"]//span/text()').getall()
            cotacao = valores_kpi[0].strip().replace("R$ ", "")
            dy = valores_kpi[1].strip().replace("%", "")
            pvp = valores_kpi[2].strip().replace("%", "")
            liquidez = valores_kpi[3].strip().split(" ")[1]
            liquidez_unidade = valores_kpi[3].strip().split(" ")[2]
            variacao = valores_kpi[4].strip().replace("%", "")
            papel = response.meta['papel']

            valores_kpi = [cotacao, dy, pvp, liquidez, liquidez_unidade, variacao, papel]

            while len(valores_kpi) < len(titulo_kpi):
                valores_kpi.append("")

            self.dados_kpi.append(dict(zip(titulo_kpi, valores_kpi)))
            
            df_kpi = pd.DataFrame(self.dados_kpi).fillna("")
            df_kpi.columns = df_kpi.columns.str.lower().str.strip().str.replace('/', '').str.replace(' ', '_')
            # Save with semicolon as separator
            df_kpi.to_csv(os.path.join(data_dir, 'fiis_kpis.csv'), index=False, sep=';', decimal=',', encoding='utf-8')


            ### INFO ###
            titulo_tabela_info = response.xpath('//div[@class="desc"]/span/text()').getall()

            titulo_info = [nome.strip() for nome in titulo_tabela_info]
            valor_patrimonial_unidade = "Valor Patrimonial Unidade"
            papel = "Papel"

            titulo_info = titulo_info + [valor_patrimonial_unidade] + [papel]
            
            valores_tabela_info = response.xpath('//div[@class="value"]/span/text()').getall()
            valores_tabela_info = [valor.strip().replace("R$ ", "").split("%")[0] for valor in valores_tabela_info]
            valor1=valores_tabela_info[0]
            valor2=valores_tabela_info[1]
            valor3=valores_tabela_info[2]
            valor4=valores_tabela_info[3]
            valor5=valores_tabela_info[4]
            valor6=valores_tabela_info[5]
            valor7=valores_tabela_info[6]
            valor8=valores_tabela_info[7]
            valor9=valores_tabela_info[8]
            valor10=valores_tabela_info[9]
            valor11=valores_tabela_info[10]
            valor12=valores_tabela_info[11]
            valor13=valores_tabela_info[12]
            valor14=valores_tabela_info[13].split(" ")[0]
            valor15=valores_tabela_info[14]
            valor16 = valores_tabela_info[13].split(" ")[1]
            papel = response.meta['papel']

            valores_tabela_info = [valor1, valor2, valor3, valor4, valor5, valor6, valor7, valor8, valor9, valor10, valor11, valor12, valor13, valor14, valor15, valor16, papel]
            while len(valores_tabela_info) < len(titulo_info):
                valores_tabela_info.append("")

            self.dados_info.append(dict(zip(titulo_info, valores_tabela_info)))

            df_info = pd.DataFrame(self.dados_info).fillna("")

            df_info.columns = df_info.columns.str.lower().str.strip().str.replace('-', '').str.replace('/', '').str.replace('.', '').str.replace(' ', '_')
            order = ['papel', 'razão_social', 'cnpj', 'público_alvo', 'mandato', 'segmento', 'tipo_de_fundo', 'prazo_de_duracao', 'tipo_de_gestao', 'taxa_de_administração', 'vacância', 'numero_de_cotistas', 'cotas_emitidas', 'val_patrimonial_p_cota', 'valor_patrimonial', 'último_rendimento', 'valor_patrimonial_unidade']
            df_info = df_info[order]
            df_info.to_csv(os.path.join(data_dir, 'fiis_info.csv'), index=False, sep=';', decimal=',', encoding='utf-8')

         
        except Exception as e:
            self.logger.error(f"Erro ao processar {response.meta['papel']}: {e}")
            

def run_fii():
    # Initialize spider and run it
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'LOG_LEVEL': 'ERROR'

    })

    # Run the spider
    process.crawl(FiiSpider)
    process.start()
    
    print("\nProcesso de coleta de dados finalizado.")


if __name__ == "__main__":
    run_fii()