from scraper.spiders.acao_spider import run_scraper
from scraper.spiders.fii_table_spider import run_fii

def get_data():
    run_scraper()
    run_fii()

get_data()
