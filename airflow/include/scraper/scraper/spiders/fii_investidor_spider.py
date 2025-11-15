import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os
#from pathlib import Path

class FiiSpider(scrapy.Spider):
    name = "fii_kpi_spider"
    allowed_domains = ["investidor10.com.br"]
    dados_kpi = []
    dados_info = []

    def start_requests(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        data_dir = os.path.join(base_dir, 'include', 'data')
        #os.makedirs(data_dir, exist_ok=True)
        df = pd.read_csv(os.path.join(data_dir,"fiis-listados-b3-tratado.csv"), quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        fiis_list = df["Papel"].tolist()
        print(f"Total de FIIs para coletar: {len(fiis_list)}")
        
        # For testing with just one FII
        #fiis_list = ["MXRF11"]
        
        for papel in fiis_list:
            url = f"https://investidor10.com.br/fiis/{papel.lower().strip()}/"
            self.logger.info(f"Requisitando dados para {papel}...")
        
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})


    async def parse(self, response):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            data_dir = os.path.join(base_dir, 'include', 'dbt_dw', 'kraken_dw', 'seed')
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
            cotacao = valores_kpi[0].strip().replace("R$ ", "").replace(".", "").replace(",", ".")
            dy = valores_kpi[1].strip().replace("%", "").replace(".", "").replace(",", ".")
            pvp = valores_kpi[2].strip().replace("%", "").replace(".", "").replace(",", ".")
            liquidez = valores_kpi[3].strip().replace(".", "").replace(",", ".").split(" ")[1]
            liquidez_unidade = valores_kpi[3].strip().split(" ")[2]
            variacao = valores_kpi[4].strip().replace("%", "").replace(".", "").replace(",", ".")
            papel = response.meta['papel']

            valores_kpi = [cotacao, dy, pvp, liquidez, liquidez_unidade, variacao, papel]

            while len(valores_kpi) < len(titulo_kpi):
                valores_kpi.append("")

            self.dados_kpi.append(dict(zip(titulo_kpi, valores_kpi)))
            
            df_kpi = pd.DataFrame(self.dados_kpi).fillna("")
            df_kpi.columns = df_kpi.columns.str.lower().str.strip().str.replace('/', '').str.replace(' ', '_')
            # Save with semicolon as separator
            df_kpi.to_csv(os.path.join(data_dir, 'fiis_kpis.csv'), index=False, sep=',', decimal='.', encoding='utf-8')


            ### INFO ###
            titulo_tabela_info = response.xpath('//div[@class="desc"]/span/text()').getall()

            titulo_info = [nome.strip() for nome in titulo_tabela_info]
            valor_patrimonial_unidade = "Valor Patrimonial Unidade"
            papel = "Papel"

            titulo_info = titulo_info + [valor_patrimonial_unidade] + [papel]
            
            valores_tabela_info = response.xpath('//div[@class="value"]/span/text()').getall()
            valores_tabela_info = [valor.strip().replace("R$ ", "").split("%")[0] for valor in valores_tabela_info]
            

            razao_social=valores_tabela_info[0]
            cnpj=valores_tabela_info[1]
            publico_alvo=valores_tabela_info[2]
            mandato=valores_tabela_info[3]
            segmento=valores_tabela_info[4]
            tipo_de_fundo=valores_tabela_info[5]
            prazo_de_duração=valores_tabela_info[6]
            tipo_de_gestão=valores_tabela_info[7]
            taxa_de_administração=valores_tabela_info[8].replace('.', '').replace(',', '.')
            vacancia=valores_tabela_info[9].replace('.', '').replace(',', '.')
            numero_de_cotistas=valores_tabela_info[10].replace('.', '').replace(',', '.')
            cotas_emitidas=valores_tabela_info[11].replace('.', '').replace(',', '.')
            val_patrimonial_p_cota=valores_tabela_info[12].replace('.', '').replace(',', '.')
            valor_patrimonial=valores_tabela_info[13].split(" ")[0].replace('.', '').replace(',', '.')
            ultimo_rendimento=valores_tabela_info[14].replace('.', '').replace(',', '.')
            valor_patrimonial_unidade=valores_tabela_info[13].split(" ")[1]
            papel = response.meta['papel']

            valores_tabela_info = [razao_social, cnpj, publico_alvo, mandato, segmento, tipo_de_fundo, prazo_de_duração, tipo_de_gestão, taxa_de_administração, vacancia, numero_de_cotistas, cotas_emitidas, val_patrimonial_p_cota, valor_patrimonial, ultimo_rendimento, valor_patrimonial_unidade, papel]
            while len(valores_tabela_info) < len(titulo_info):
                valores_tabela_info.append("")

            self.dados_info.append(dict(zip(titulo_info, valores_tabela_info)))

            df_info = pd.DataFrame(self.dados_info).fillna("")

            df_info.columns = df_info.columns.str.lower().str.strip().str.replace('-', '_').str.replace('/', '').str.replace('.', '').str.replace(' ', '_')
            df_info.to_csv(os.path.join(data_dir, 'fiis_info.csv'), index=False, sep=',', decimal='.', encoding='utf-8')

         
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