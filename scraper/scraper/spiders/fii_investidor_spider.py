import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os
import sys
import django
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
mysite_path = os.path.join(project_root, 'mysite')
settings_path = os.path.join(mysite_path, 'mysite', 'settings.py')

# Imprime informações de depuração
print(f"Project root: {project_root}")
print(f"Mysite path: {mysite_path}")
print(f"Settings path: {settings_path}")
print(f"Current working directory: {os.getcwd()}")

# Adiciona o diretório do projeto ao PYTHONPATH
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Verifica se o arquivo de configurações existe
if not os.path.exists(settings_path):
    print(f"Erro: O arquivo de configurações {settings_path} não foi encontrado.")
    DJANGO_AVAILABLE = False
else:
    # Define a variável de ambiente para o módulo de configurações do Django
    settings_module = 'mysite.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    print(f"Usando módulo de configurações: {settings_module}")
    
    try:
        # Adiciona o diretório pai do mysite ao PYTHONPATH
        parent_dir = os.path.dirname(mysite_path)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Adiciona o diretório do projeto Django ao PYTHONPATH
        if mysite_path not in sys.path:
            sys.path.insert(0, mysite_path)
        
        # Imprime os caminhos para depuração
        print(f"Python path: {sys.path}")
        
        # Verifica se o módulo fiis pode ser importado
        try:
            import fiis
            print(f"Módulo fiis encontrado em: {os.path.dirname(fiis.__file__)}")
        except ImportError as e:
            print(f"Erro ao importar módulo fiis: {e}")
        
        # Configura o Django
        django.setup()
        from fiis.models import FiisKpi, FiisInfo
        print("Django configurado com sucesso!")
        DJANGO_AVAILABLE = True
    except Exception as e:
        import traceback
        print(f"Erro ao configurar o Django: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        print("Os dados serão salvos em um arquivo CSV em vez do banco de dados.")
        DJANGO_AVAILABLE = False


class FiiSpider(scrapy.Spider):
    name = "fii_kpi_spider"
    allowed_domains = ["investidor10.com.br"]
    dados_kpi = []
    dados_info = []

    def start_requests(self):
        
        df = pd.read_csv(f"{project_root}/fiis-listados-b3-tratado.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        fiis_list = df["Papel"].tolist()
        
        # For testing with just one FII
        #fiis_list = ["MXRF11"]
        
        for papel in fiis_list:
            url = f"https://investidor10.com.br/fiis/{papel.lower().strip()}/"
            self.logger.info(f"Requisitando dados para {papel}...")
        
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})


    def parse(self, response):
        try:
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
            # Save with semicolon as separator
            df_kpi.to_csv(f"{project_root}/fiis_kpis.csv", index=False, sep=';', decimal=',', encoding='utf-8')


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

            df_info.to_csv(f"{project_root}/fiis_info.csv", index=False, sep=';', decimal=',', encoding='utf-8')

         
        except Exception as e:
            self.logger.error(f"Erro ao processar {response.meta['papel']}: {e}")
            
def salvar_kpis(df_kpi):
    # Mapeia os campos do item para o modelo Fiis
    campos_kpi_map = {
        'Papel': 'papel',
        'Cotação': 'cotacao',
        'DY': 'dy_12m',
        'P/VP': 'pvp',
        'Liquidez Diária': 'liquidez_diaria',
        'Liquidez Unidade': 'liquidez_diaria_unidade',
        'VARIAÇÃO': 'variacao_12m',
    }
    
    # Processa cada linha do DataFrame
    for _, row in df_kpi.iterrows():
        try:
            papel = str(row['Papel']).strip()

            dados = {}
            

            for col, campo in campos_kpi_map.items():
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    valor = str(row[col]).strip()
                    
                    # Skip empty or special values
                    if valor in ('', '-', 'não disponível', 'não há dados', 'N/A'):
                        dados[campo] = None
                        continue

                    # Get the field type from the model
                    field = FiisKpi._meta.get_field(campo)
            
            # Atualiza ou cria o registro no banco de dados
            FiisKpi.objects.update_or_create(
                papel=papel,
                defaults=dados
            )
            print(f"Dados para {papel} salvos com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar {papel}: {str(e)}")

def salvar_info(df_info):
    campos_info_map = {
        'Papel': 'papel',
        'Razão Social': 'razao_social',
        'CNPJ': 'cnpj',
        'PÚBLICO-ALVO': 'publico_alvo',
        'MANDATO': 'mandato',
        'SEGMENTO': 'segmento',
        'TIPO DE FUNDO': 'tipo_fundo',
        'PRAZO DE DURAÇÃO': 'prazo_duracao',
        'TIPO DE GESTÃO': 'tipo_gestao',
        'TAXA DE ADMINISTRAÇÃO': 'taxa_administracao',
        'VACÂNCIA': 'vacancia',
        'NUMERO DE COTISTAS': 'numero_cotistas',
        'COTAS EMITIDAS': 'cotas_emitidas',
        'VAL. PATRIMONIAL P/ COTA': 'valor_patrimonial_cota',
        'VALOR PATRIMONIAL': 'valor_patrimonial',
        'ÚLTIMO RENDIMENTO': 'ultimo_rendimento',
        'Valor Patrimonial Unidade': 'valor_patrimonial_unidade'
    }
    
    for _, row in df_info.iterrows():
        try:
            papel = str(row['Papel']).strip()

            dados = {}
            
            for col, campo in campos_info_map.items():
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    valor = str(row[col]).strip()
                    
                    # Skip empty or special values
                    if valor in ('', '-', 'não disponível', 'não há dados', 'N/A'):
                        dados[campo] = None
                        continue

                    # Get the field type from the model
                    field = FiisInfo._meta.get_field(campo)
            
            # Atualiza ou cria o registro no banco de dados
            FiisInfo.objects.update_or_create(
                papel=papel,
                defaults=dados
            )
            print(f"Dados para {papel} salvos com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar {papel}: {str(e)}")

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

    df_kpi = pd.read_csv(f"{project_root}/fiis_kpis.csv", sep=';',thousands='.', decimal=',', encoding='utf-8')
    df_info = pd.read_csv(f"{project_root}/fiis_info.csv", sep=';',thousands='.', decimal=',', encoding='utf-8')

    # Tenta salvar no banco de dados se o Django estiver disponível
    if DJANGO_AVAILABLE and not df_kpi.empty and not df_info.empty:
        try:
            salvar_kpis(df_kpi)
            salvar_info(df_info)
            print("Todos os dados foram salvos no banco de dados com sucesso!")
            return
        except Exception as e:
            import traceback
            print(f"Erro ao salvar no banco de dados: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("Tentando salvar em um arquivo CSV...")

if __name__ == "__main__":
    run_fii()