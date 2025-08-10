import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do navegador
options = Options()
options.add_argument("--headless")  # Executa em modo headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")

# Inicializar o WebDriver
driver = webdriver.Chrome(options=options)

try:
    # Acessar a URL
    url = "https://www.fundsexplorer.com.br/ranking"
    driver.get(url)
    
    # Esperar a tabela carregar
    wait = WebDriverWait(driver, 10)
    table = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='upTo--default-fiis-table']/div/table"))
    )
    
    # Dar um tempo adicional para garantir que tudo esteja carregado
    #time.sleep(5)
    
    # Obter o HTML da tabela
    html_content = table.get_attribute("outerHTML")
    
    # Usar BeautifulSoup para processar o HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extrair os dados da tabela
    data = []
    table = soup.find('table')
    
    # Extrair cabeçalhos
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Extrair linhas
    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        data.append([col.text.strip().replace("%", "").replace("N/A", "").replace(".","").replace(",", ".") for col in cols])
    
    # Criar DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Salvar em CSV
    df.to_csv('fundos_imobiliarios.csv', index=False)
    print("Dados salvos com sucesso em 'fundos_imobiliarios.csv'")
    
except Exception as e:
    print(f"Ocorreu um erro: {str(e)}")
    
finally:
    # Fechar o navegador
    driver.quit()