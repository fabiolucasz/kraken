import pandas as pd
import sys
import django
import time
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
        from fiis.models import FiisFundsExplorer
        print("Django configurado com sucesso!")
        DJANGO_AVAILABLE = True
    except Exception as e:
        import traceback
        print(f"Erro ao configurar o Django: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        print("Os dados serão salvos em um arquivo CSV em vez do banco de dados.")
        DJANGO_AVAILABLE = False
  
def scrape_funds_explorer():
    try:
        print("\nIniciando coleta da tabela de fundos...")
        
        # Configuração do Selenium
        options = Options()
        options.add_argument("--headless")
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
            data.append([col.text.strip().replace("%", "").replace("N/A", "") for col in cols])
        
        df = pd.DataFrame(data, columns=headers).fillna("")
        df = df.rename(columns={"Fundos": "Papel"})
        df = df.drop(columns=["Tax. Gestão", "Tax. Performance", "Tax. Administração", "P/VP"])
        

        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        output_path = os.path.join(os.path.dirname(__file__), 'data/fiis_funds.csv')
        df.to_csv(output_path, sep=';', decimal=',', index=False, encoding='utf-8')

        if not data:
            raise Exception("Nenhum dado encontrado na tabela")
        
    except Exception as e:
        print(f"\nErro ao coletar dados do Funds Explorer: {str(e)}")
        if driver:
            driver.save_screenshot('error_funds_explorer.png')
            print("Screenshot salvo como 'error_funds_explorer.png'")
    finally:
        if driver:
            driver.quit()

def salvar_no_banco(df):
    # Mapeia os campos do item para o modelo Fiis
    campos_map = {
        'Papel': 'papel',
        'Setor': 'setor',
        'Preço Atual (R$)': 'cotacao',
        'Liquidez Diária (R$)': 'liquidez_diaria_rs',
        'Último Dividendo': 'ultimo_dividendo',
        'Dividend Yield': 'dividend_yield',
        'DY (3M) Acumulado': 'dy_3m_acumulado',
        'DY (6M) Acumulado': 'dy_6m_acumulado',
        'DY (12M) Acumulado': 'dy_12m_acumulado',
        'DY (3M) média': 'dy_3m_media',
        'DY (6M) média': 'dy_6m_media',
        'DY (12M) média': 'dy_12m_media',
        'DY Ano': 'dy_ano',
        'Variação Preço': 'variacao_preco',
        'Rentab. Período': 'rentab_periodo',
        'Rentab. Acumulada': 'rentab_acumulada',
        'Patrimônio Líquido': 'patrimonio_liquido',
        'VPA': 'vpa',
        'P/VPA': 'p_vpa',
        'DY Patrimonial': 'dy_patrimonial',
        'Variação Patrimonial': 'variacao_patrimonial',
        'Rentab. Patr. Período': 'rentab_patr_periodo',
        'Rentab. Patr. Acumulada': 'rentab_patr_acumulada',
        'Quant. Ativos': 'quant_ativos',
        'Volatilidade': 'volatilidade',
        'Num. Cotistas': 'num_cotistas',
    }
    # Processa cada linha do DataFrame
    for _, row in df.iterrows():
        try:
            papel = str(row['Papel']).strip()

            dados = {}
            
            # Processa cada campo
            for col, campo in campos_map.items():
                if col not in row or pd.isna(row[col]) or str(row[col]).strip() == '':
                    dados[campo] = None
                    continue
                    
                valor = str(row[col]).strip()
                
                # Pula valores vazios ou inválidos
                if valor.lower() in ('', '-', 'não disponível', 'não há dados', 'n/a'):
                    dados[campo] = None
                    continue
                
                # Processa campos numéricos
                if campo not in ['papel', 'setor']:
                    try:
                        # Remove caracteres não numéricos, exceto sinal negativo, ponto e vírgula
                        clean_val = ''.join(c for c in valor if c in '0123456789-.,')
                        # Remove pontos de milhar e converte vírgula para ponto
                        clean_val = clean_val.replace('.', '').replace(',', '.')
                        valor_float = float(clean_val)
                        # Converte para inteiro se for um campo de contagem
                        if campo in ['quant_ativos', 'num_cotistas']:
                            dados[campo] = int(round(valor_float))
                        else:
                            dados[campo] = round(valor_float, 6)  # Arredonda para 6 casas decimais
                    except (ValueError, TypeError):
                        dados[campo] = None
                else:
                    # Campos de texto
                    dados[campo] = valor

            # Atualiza ou cria o registro no banco de dados
            FiisFundsExplorer.objects.update_or_create(
                papel=papel,
                defaults=dados
            )
            print(f"Dados para {papel} salvos com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar {papel}: {str(e)}")

def run_fii_fundsexplorer():
  
    scrape_funds_explorer()
    

    print("\nProcesso de coleta de dados finalizado.")

    # Read from the data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    df = pd.read_csv(os.path.join(data_dir, 'fiis_funds.csv'), sep=';', decimal=',', encoding='utf-8')

    # Tenta salvar no banco de dados se o Django estiver disponível
    if DJANGO_AVAILABLE and not df.empty:
        try:
            salvar_no_banco(df)
            print("Todos os dados foram salvos no banco de dados com sucesso!")
            return
        except Exception as e:
            import traceback
            print(f"Erro ao salvar no banco de dados: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("Tentando salvar em um arquivo CSV...")


if __name__ == "__main__":
    run_fii_fundsexplorer()