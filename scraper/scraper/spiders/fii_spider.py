import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from datetime import datetime
import sys
import django
from pathlib import Path
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Configurar Django para poder usar os modelos
# Obtém o diretório raiz do projeto (o diretório que contém a pasta 'mysite')
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
        from fiis.models import Fiis
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
    name = "fii_spider"
    allowed_domains = ["investidor10.com.br"]
    dados_grid = []
    dados_info = []

    def start_requests(self):
        
        df = pd.read_csv("fiis-listados-b3-tratado.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
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
            titulos_grid = response.xpath('//div[@class="_card-header"]//div//span/text()').getall()
            if len(titulos_grid) < 6:
                
                titulo_cotacao = titulos_grid[0].strip().split(" ")[1]
                titulo_dy = titulos_grid[1].strip().split(" ")[1]
                titulo_pvp = titulos_grid[2].strip()
                titulo_liquidez = titulos_grid[3].strip()
                titulo_liquidez_unidade = "Liquidez Unidade"
                titulo_variacao = titulos_grid[4].strip().split(" ")[0]
                titulo_papel = "Papel"
                titulo_grid = [titulo_cotacao, titulo_dy, titulo_pvp, titulo_liquidez, titulo_liquidez_unidade, titulo_variacao, titulo_papel]

                valores_grid = response.xpath('//div[@class="_card-body"]//span/text()').getall()
                cotacao = valores_grid[0].strip().replace("R$ ", "").replace(",", ".")
                dy = valores_grid[1].strip().replace("%", "").replace(",", ".")
                pvp = valores_grid[2].strip().replace("%", "").replace(",", ".")
                liquidez = valores_grid[3].strip().split(" ")[1].replace(",", ".")
                liquidez_unidade = valores_grid[3].strip().split(" ")[2]
                variacao = valores_grid[4].strip().replace("%", "").replace(",", ".")
                papel = response.meta['papel']

                valores_grid = [cotacao, dy, pvp, liquidez, liquidez_unidade, variacao, papel]

                while len(valores_grid) < len(titulo_grid):
                    valores_grid.append("")

                self.dados_grid.append(dict(zip(titulo_grid, valores_grid)))

            else:
                print("Títulos do grid a mais que o esperado")


            titulo_tabela_info = response.xpath('//div[@class="desc"]/span/text()').getall()
            if len(titulo_tabela_info) <= 17:
                
                titulo_info = [nome.strip() for nome in titulo_tabela_info]
                valor_patrimonial_unidade = "Valor Patrimonial Unidade"
                papel = "Papel"

                titulo_info = titulo_info + [valor_patrimonial_unidade] + [papel]



                valores_tabela_info = response.xpath('//div[@class="value"]/span/text()').getall()
                valores_tabela_info = [valor.strip().replace(".", "").replace(",", ".").replace("R$ ", "").split("%")[0] for valor in valores_tabela_info]
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

                print(f"{papel} coletado com sucesso")

                df1 = pd.DataFrame(self.dados_grid).fillna("")
                df2 = pd.DataFrame(self.dados_info).fillna("")
                df = pd.merge(df1, df2)
                df.to_csv("fiis_detailed.csv", index=False)
                print("Dados Salvos com sucesso!")

            else:
                print(f"{papel}: Não foi possível coletar informações adicionais")
            
            
                
        except Exception as e:
            self.logger.error(f"Erro ao processar {response.meta['papel']}: {e}")
            

    
def scrape_funds_explorer():
    try:
        print("\nIniciando coleta da tabela de fundos...")
        
        # Configuração do Selenium
        options = Options()
        #options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-minimized")

        service = Service()
        url_funds = "https://www.fundsexplorer.com.br/ranking"

        # Inicializa o driver
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Acessando a página...")
        driver.get(url_funds)
        
        # Espera explícita para garantir que a página foi carregada
        wait = WebDriverWait(driver, 20)
        
        print("Aguardando carregamento da tabela...")
        # Primeiro espera o elemento ficar presente na página
        table_locator = (By.XPATH, "//*[@id='upTo--default-fiis-table']/div/table")
        table = wait.until(EC.presence_of_element_located(table_locator))
        wait.until(EC.visibility_of(table))
        time.sleep(2)  # Pequena pausa para garantir o carregamento
        
        # Extrai o HTML da tabela
        html_content = table.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Processa os dados da tabela
        data = []
        table = soup.find('table')
        if not table:
            raise Exception("Tabela não encontrada no HTML")
        
        headers = [th.text.strip() for th in table.find_all('th')]
        
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            while len(cols) < len(headers):
                cols.append("")
            data.append([col.text.strip().replace("%", "").replace("N/A", "").replace(".","").replace(",", ".") for col in cols])
        
        if not data:
            raise Exception("Nenhum dado encontrado na tabela")
        

        df = pd.DataFrame(data, columns=headers)
        df = df.rename(columns={"Fundos": "Papel"})
        df = df.drop(columns=["Tax. Gestão", "Tax. Performance", "Tax. Administração", "P/VP"])
        
        output_file = 'fiis_table.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Dados salvos com sucesso em '{output_file}'")
        return True
        
    except Exception as e:
        print(f"\nErro ao coletar dados do Funds Explorer: {str(e)}")
        if driver:
            driver.save_screenshot('error_funds_explorer.png')
            print("Screenshot salvo como 'error_funds_explorer.png'")
    finally:
        if driver:
            driver.quit()

def merge_datasets():
    try:
       df1 = pd.read_csv("fiis_detailed.csv", encoding='utf-8')
       df2 = pd.read_csv("fiis_table.csv", encoding='utf-8')
       df = pd.merge(df2, df1, on="Papel", how="left")
       df.to_csv("fiis.csv", index=False, encoding='utf-8')
       print("Dados mesclados com sucesso!")
       os.remove("fiis_detailed.csv")
       os.remove("fiis_table.csv")
       return df
            
    except Exception as e:
        print(f"\nErro ao mesclar os dados: {str(e)}")
        

def salvar_no_banco(df):
    # Mapeia os campos do item para o modelo Fiis
    campos_map = {
        'papel': 'papel',
        'cotacao': 'cotacao',
        'dividend_yield': 'dy',
        'p_vp': 'pvp',
        'liquidez_diaria': 'liquidez',
        'variacao': 'variacao',
        'dy_pago_ult_12m': 'dy_pago_ult_12m',
        'setor': 'setor',
        'tipo': 'tipo',
        'taxa_administracao': 'taxa_administracao',
        'vacancia': 'vacancia',
        'valor_patrimonial': 'valor_patrimonial',
        'ultimo_rendimento': 'ultimo_rendimento',
        'num_cotistas': 'num_cotistas',
        'cotas_emitidas': 'cotas_emitidas',
    }
    # Processa cada linha do DataFrame
    for _, row in df.iterrows():
        try:
            papel = str(row['Papel']).strip()
            print(f"Processando registro para {papel}")
            
            # Cria um dicionário para armazenar os dados
            dados = {}
            
            # Processa cada campo
            for col, campo in campos_map.items():
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    valor = str(row[col]).strip()
                    
                    # Converte valores vazios ou inválidos para None
                    if valor in ('', '-', 'não disponível', 'não há dados', 'N/A'):
                        dados[campo] = None
                        continue
                        
                    # Remove caracteres especiais
                    valor = valor.replace('%', '').replace('R$', '').replace('.', '').replace(',', '.').strip()
                    
                    # Tenta converter para o tipo apropriado
                    try:
                        # Tenta converter para Decimal primeiro
                        try:
                            dados[campo] = Decimal(valor)
                        except:
                            # Se falhar, tenta converter para inteiro
                            try:
                                dados[campo] = int(float(valor))
                            except:
                                # Se ainda falhar, mantém como string
                                dados[campo] = valor
                    except:
                        dados[campo] = valor
            
            # Atualiza ou cria o registro no banco de dados
            Fiis.objects.update_or_create(
                papel=papel,
                defaults=dados
            )
            print(f"Dados para {papel} salvos com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar {papel}: {str(e)}")
    

def run_fii():
    # Initialize spider and run it
    spider = FiiSpider()
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'LOG_LEVEL': 'ERROR'

    })

    # Run the spider
    # process.crawl(FiiSpider)
    # process.start()
    
    # After spider finishes, run the funds explorer scraper
    print("\nIniciando coleta do Funds Explorer...")
    scrape_funds_explorer()
    
   
    merge_datasets()

    print("\nProcesso de coleta de dados finalizado.")

    df = pd.read_csv("fiis.csv", encoding='utf-8')

    # Tenta salvar no banco de dados se o Django estiver disponível
    # if DJANGO_AVAILABLE and not df.empty:
    #     try:
    #         salvar_no_banco(df)
    #         print("Todos os dados foram salvos no banco de dados com sucesso!")
    #         return
    #     except Exception as e:
    #         import traceback
    #         print(f"Erro ao salvar no banco de dados: {e}")
    #         print("Traceback:")
    #         traceback.print_exc()
    #         print("Tentando salvar em um arquivo CSV...")
    
    # # Se o Django não estiver disponível, ocorrer um erro ou não houver dados, salva em um arquivo CSV
    # if not df.empty:
    #     output_file = "fiis.csv"
    #     df.to_csv(output_file, index=False, encoding='utf-8')
    #     print(f"Dados salvos em {output_file}")
    # else:
    #     print("Nenhum dado disponível para salvar.")




def remover_segundo_ponto(val):
    if pd.isna(val):
        return val
    val = str(val).strip()
    val = val.replace(',', '.')        
    partes = val.split('.')           
    if len(partes) > 2:
        return '.'.join(partes[:-1]) + partes[-1]
    return val
    



run_fii()
