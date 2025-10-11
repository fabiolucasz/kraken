import pandas as pd
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

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

def run_fii_fundsexplorer():
  
    scrape_funds_explorer()
    

    print("\nProcesso de coleta de dados finalizado.")

    # Read from the data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    df = pd.read_csv(os.path.join(data_dir, 'fiis_funds.csv'), sep=';', decimal=',', encoding='utf-8')

    # Salvar CSV no diretório do Airflow
    if not df.empty:
        df.to_csv('/usr/local/airflow/data/fiis_funds.csv', index=False, sep=';', decimal=',', encoding='utf-8')
        print("Dados salvos em /usr/local/airflow/data/fiis_funds.csv")


if __name__ == "__main__":
    run_fii_fundsexplorer()