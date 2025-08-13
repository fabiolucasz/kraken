import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    # Configuração mais robusta do ChromeDriver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    driver = None
    try:
        # Inicializa o driver
        driver = setup_driver()
        url = "https://www.fundsexplorer.com.br/ranking"
        
        print("Acessando a página...")
        driver.get(url)
        
        # Espera explícita para garantir que a página foi carregada
        wait = WebDriverWait(driver, 20)
        
        print("Aguardando carregamento da tabela...")
        # Primeiro espera o elemento ficar presente na página
        table_locator = (By.XPATH, "//*[@id='upTo--default-fiis-table']/div/table")
        table = wait.until(EC.presence_of_element_located(table_locator))
        
        # Depois espera que a tabela esteja visível
        wait.until(EC.visibility_of(table))
        
        # Pequena pausa para garantir que todos os dados foram carregados
        time.sleep(2)
        
        html_content = table.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data = []
        table = soup.find('table')
        
        if not table:
            raise Exception("Tabela não encontrada no HTML")
            
        headers = [th.text.strip() for th in table.find_all('th')]
        
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            data.append([col.text.strip().replace("%", "").replace("N/A", "").replace(".","").replace(",", ".") for col in cols])
        
        if not data:
            raise Exception("Nenhum dado encontrado na tabela")
            
        df = pd.DataFrame(data, columns=headers)
        
        output_file = 'fiis.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Dados salvos com sucesso em '{output_file}'")
        return True
        
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        # Tira um print da tela para debug
        if driver:
            driver.save_screenshot('error_screenshot.png')
            print("Screenshot salvo como 'error_screenshot.png'")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("Driver fechado")

if __name__ == "__main__":
    main()