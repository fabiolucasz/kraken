from bs4 import BeautifulSoup
import pandas as pd
import asyncio
from playwright.async_api import async_playwright, Playwright
import os

# Global variable to store the scraped data
scraped_data = None

async def fetch_data(playwright: Playwright):
    """Async function to fetch data from the website"""
    global scraped_data
    chromium = playwright.chromium
    browser = await chromium.launch()
    page = await browser.new_page()
    
    try:
        await page.goto("https://www.fundsexplorer.com.br/ranking")
        await page.wait_for_selector("div table tbody tr:nth-child(100)", state="attached", timeout=100000)
        table = await page.content()
        soup = BeautifulSoup(table, "html.parser")
        
        # Process the table data
        data = []
        table = soup.find('table')
        if not table:
            raise Exception("Tabela não encontrada no HTML")
        
        headers = [th.text.strip() for th in table.find_all('th')]
        
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            while len(cols) < len(headers):
                cols.append("")
            data.append([col.text.strip().replace("%", "").replace("N/A", "").replace(".", "").replace(",", ".") for col in cols])
        
        # Store the processed data in the global variable
        scraped_data = pd.DataFrame(data, columns=headers).fillna("")
        scraped_data = scraped_data.rename(columns={"Fundos": "Papel"})
        print(f"scraped_data: {scraped_data}")
        
    finally:
        await browser.close()

def save_to_csv(output_path=None):
    """Synchronous function to save data to CSV"""
    global scraped_data
    if scraped_data is None:
        raise Exception("Nenhum dado foi coletado ainda. Execute fetch_data() primeiro.")
    
    if output_path is None:
        # Default output path if none provided
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
        print(f"base_dir: {base_dir}")
        data_dir = os.path.join(base_dir, 'local', 'airflow', 'dbt_dw', 'kraken_dw', 'seeds')
        print(f"data_dir: {data_dir}")
        output_path = os.path.join(data_dir, "fiis_fundsexplorer_final.csv")
    
    # Create directory if it doesn't exist
    #os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    scraped_data.to_csv(output_path, sep=',', decimal='.', index=False, encoding='utf-8')
    print(f"scraped_data saved: {scraped_data}")
    print(f"Arquivo salvo em: {output_path}")

async def run_fii_fundsexplorer():
    """Main async function to run the scraper"""
    async with async_playwright() as playwright:
        await fetch_data(playwright)

def start_crawl(output_path=None):
    """Synchronous entry point that handles the async execution"""
    global scraped_data
    asyncio.run(run_fii_fundsexplorer())
    if scraped_data is not None:
        save_to_csv(output_path)
    else:
        print("Nenhum dado foi coletado.")

if __name__ == "__main__":
    start_crawl()