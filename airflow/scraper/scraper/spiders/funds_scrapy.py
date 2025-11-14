import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import pandas as pd

class FundsexplorerSpider(scrapy.Spider):
    name = "fundsexplorer"
    
    allowed_domains = ["www.fundsexplorer.com.br"]

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': False,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }


    def start_requests(self):
        url = "https://www.fundsexplorer.com.br/ranking"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div table tbody tr:nth-child(100)", state="attached", timeout=10000),
                    PageMethod("wait_for_timeout", 100000),

            
            ],
        
        })

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_selector("div table tbody tr:nth-child(100)", state="attached", timeout=100000)
        table = response.css("table").get()
        soup = BeautifulSoup(table, "html.parser")
        table = soup.find("table")

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
            data.append([col.text.strip().replace("%", "").replace("N/A", "").replace(".", "").replace(",", ".") for col in cols])
        
        df = pd.DataFrame(data, columns=headers).fillna("")
        df = df.rename(columns={"Fundos": "Papel"})
        

        # Create data directory if it doesn't exist
        #os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
        print(f"Base dir: {base_dir}")
        output_path = os.path.join(base_dir, 'data')
        print(f"Output path: {output_path}")
        df.to_csv(os.path.join(output_path, "fiis_funds.csv"), sep=',', decimal='.', index=False, encoding='utf-8')
        print(f"File saved to: {os.path.join(output_path, "fiis_funds.csv")}")
        #df.to_csv("fiis_funds_playwright.csv", sep=',', decimal='.', index=False, encoding='utf-8')

        print(soup)

def main():
    process = CrawlerProcess(settings={"LOG_LEVEL": "ERROR"})
    process.crawl(FundsexplorerSpider)
    process.start()

if __name__ == "__main__":
    main()