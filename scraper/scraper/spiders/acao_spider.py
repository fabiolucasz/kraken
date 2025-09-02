import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import os
import sys
import django
from decimal import Decimal, InvalidOperation
from django.db import models

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
mysite_path = os.path.join(project_root, 'mysite')
settings_path = os.path.join(mysite_path, 'mysite', 'settings.py')


if project_root not in sys.path:
    sys.path.insert(0, project_root)


if not os.path.exists(settings_path):
    print(f"Erro: O arquivo de configurações {settings_path} não foi encontrado.")
    DJANGO_AVAILABLE = False
else:
    settings_module = 'mysite.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    try:
        parent_dir = os.path.dirname(mysite_path)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if mysite_path not in sys.path:
            sys.path.insert(0, mysite_path)
        
        try:
            import acoes
            print(f"Módulo acoes encontrado em: {os.path.dirname(acoes.__file__)}")
        except ImportError as e:
            print(f"Erro ao importar módulo acoes: {e}")
        
        django.setup()
        from acoes.models import Acoes
        print("Django configurado com sucesso!")
        DJANGO_AVAILABLE = True
    except Exception as e:
        import traceback
        print(f"Erro ao configurar o Django: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        DJANGO_AVAILABLE = False


class AcaoSpider(scrapy.Spider):
    name = "acao_spider"
    allowed_domains = ["investidor10.com.br"]

    dados_kpi = []
    dados_indicadores = []
    dados_info = []
    dados_img = []

    def start_requests(self):
        df = pd.read_csv(f"{project_root}/acoes-listadas-b3.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
        for papel in df['Ticker']:
            url = f"https://investidor10.com.br/acoes/{papel.lower()}/"
            yield scrapy.Request(url, callback=self.parse, meta={'papel': papel})

    def parse(self, response):
        try:
            papel = response.meta['papel']

            #Link da imagem
            img = response.css('div#container-ticker-data img::attr(src)').getall()
            img = img[0]
            ticker_img = response.urljoin(img)
            while len(ticker_img) < len(papel):
                ticker_img.append(" ")
            self.dados_img.append(dict(zip(["Papel", "Ticker_Img"], [papel, ticker_img])))

            # KPIs
            kpis = [k.strip().replace(" ", "_") for k in response.css('div._card-header div span::text').getall() if k.strip()]
            kpi_values = [v.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(",", ".") for v in response.css('div._card-body span::text').getall() if v.strip()]
            while len(kpi_values) < len(kpis):
                kpi_values.append("")
            self.dados_kpi.append(dict(zip(kpis, kpi_values), Papel=papel))

            # Indicadores
            indicadores = [i.strip().replace(" ", "_").replace(f"DIVIDEND_YIELD__-_{response.meta['papel']}", "DY") for i in response.css('div.cell span.d-flex::text').getall() if i.strip()]
            indicadores_values = [iv.strip().replace(".", "").replace(",", ".").replace("%", "") for iv in response.css('div.value span::text').getall() if iv.strip()]
            while len(indicadores_values) < len(indicadores):
                indicadores_values.append("")
            self.dados_indicadores.append(dict(zip(indicadores, indicadores_values), Papel=papel))

            # Informações da ação
            info = [i.strip().replace(" ", "_").replace("Segmento_de_Listagem", "Liquidez_Média_Diária").replace("Free_Float", "Segmento_de_Listagem").replace("Tag_Along", "Free_Float").replace("Liquidez_Média_Diária", "Tag_Along") for i in response.css('div.cell span.title::text').getall() if i.strip()]
            info_values_div = [iv.strip().replace(" ", "").replace("%", "").replace("R$", "").replace(".", "").replace(",", ".") for iv in response.css('span.value div.detail-value::text').getall() if iv.strip()]
            info_values_text = [iv.strip().replace(" ", "_").replace("%", "").replace("R$", "").replace(",", ".") for iv in response.css('div.cell span.value::text').getall() if iv.strip()]
            info_values = info_values_div + info_values_text
            while len(info_values) < len(info):
                info_values.append("")
            self.dados_info.append(dict(zip(info, info_values), Papel=papel))

            df1 = pd.DataFrame(self.dados_kpi).fillna("")
            #df1.to_csv("acoes_kpi_debug.csv", index=False)
            df2 = pd.DataFrame(self.dados_indicadores).fillna("")
            #df2.to_csv("acoes_indicadores_debug.csv", index=False)
            df3 = pd.DataFrame(self.dados_info).fillna("")
            #df3.to_csv("acoes_info_debug.csv", index=False)
            df4 = pd.DataFrame(self.dados_img).fillna("")
            #df4.to_csv("acoes_img_debug.csv", index=False)

            df = pd.merge(df1, df2).merge(df3).merge(df4)
            df['P/L'] = df['P/L'].apply(remover_segundo_ponto)
            df['PAYOUT'] = df['PAYOUT'].apply(remover_segundo_ponto)
            df['ROE'] = df['ROE'].apply(remover_segundo_ponto)
            df = df.drop(columns=["carteira_investidor_10"])
            df = df.applymap(lambda x: "" if x == "-" else x)

            return df

            
            
        except Exception as e:
            self.logger.error(f"Erro ao processar {papel}: {e}")

def salvar_no_banco(df):

    campos_map = {
        'Cotação': 'cotation',
        'VARIAÇÃO_(12M)': 'variation_12m',
        'P/L': 'pl',
        'P/VP': 'pv',
        'DY': 'dy',
        'Papel': 'papel',
        'P/RECEITA_(PSR)': 'psr',
        'PAYOUT': 'payout',
        'MARGEM_LÍQUIDA': 'margem_liquida',
        'MARGEM_BRUTA': 'margem_bruta',
        'MARGEM_EBIT': 'margem_ebit',
        'MARGEM_EBITDA': 'margem_ebitda',
        'EV/EBITDA': 'ev_ebitda',
        'EV/EBIT': 'ev_ebit',
        'P/EBITDA': 'pebitda',
        'P/EBIT': 'pebit',
        'P/ATIVO': 'pativo',
        'P/CAP.GIRO': 'p_cap_giro',
        'P/ATIVO_CIRC_LIQ': 'p_ativo_circ_liq',
        'VPA': 'vpa',
        'LPA': 'lpa',
        'GIRO_ATIVOS': 'giro_ativos',
        'ROE': 'roe',
        'ROIC': 'roic',
        'ROA': 'roa',
        'DÍVIDA_LÍQUIDA_/_PATRIMÔNIO': 'divida_liquida_patrimonio',
        'DÍVIDA_LÍQUIDA_/_EBITDA': 'divida_liquida_ebitda',
        'DÍVIDA_LÍQUIDA_/_EBIT': 'divida_liquida_ebit',
        'DÍVIDA_BRUTA_/_PATRIMÔNIO': 'divida_bruta_patrimonio',
        'PATRIMÔNIO_/_ATIVOS': 'patrimonio_ativos',
        'PASSIVOS_/_ATIVOS': 'passivos_ativos',
        'LIQUIDEZ_CORRENTE': 'liquidez_corrente',
        'CAGR_RECEITAS_5_ANOS': 'cagr_receitas_5_anos',
        'CAGR_LUCROS_5_ANOS': 'cagr_lucros_5_anos',
        'Valor_de_mercado': 'valor_mercado',
        'Valor_de_firma': 'valor_firma',
        'Patrimônio_Líquido': 'patrimonio_liquido',
        'Nº_total_de_papeis': 'numero_papeis',
        'Ativos': 'ativos',
        'Ativo_Circulante': 'ativo_circulante',
        'Dívida_Bruta': 'divida_bruta',
        'Dívida_Líquida': 'divida_liquida',
        'Disponibilidade': 'disponibilidade',
        'Segmento_de_Listagem': 'segmento_listagem',
        'Free_Float': 'free_float',
        'Setor': 'setor',
        'Segmento': 'segmento',
        'Ticker_Img': 'ticker_img',
        'Tag_Along': 'tag_along',
    }

    for _, row in df.iterrows():
        try:
            papel = str(row['Papel']).strip()

            dados = {}
            

            for col, campo in campos_map.items():
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    valor = str(row[col]).strip()
                    
                    # Skip empty or special values
                    if valor in ('', '-', 'não disponível', 'não há dados', 'N/A'):
                        dados[campo] = None
                        continue

                    # Get the field type from the model
                    field = Acoes._meta.get_field(campo)
                    
                    # Handle different field types appropriately
                    try:
                        if isinstance(field, (models.DecimalField, models.FloatField, models.IntegerField)):
                            # For numeric fields, clean the value and convert to appropriate type
                            clean_val = valor.strip()
                            
                            # Remove percentage and currency symbols
                            clean_val = clean_val.replace('%', '').replace('R$', '').strip()
                            
                            # Handle different decimal/thousand separators
                            if '.' in clean_val and ',' in clean_val:
                                # Format: 1.000,50 (thousands separator and decimal comma)
                                clean_val = clean_val.replace('.', '').replace(',', '.')
                            elif ',' in clean_val and clean_val.count(',') == 1:
                                # Format: 1000,50 (just decimal comma)
                                clean_val = clean_val.replace(',', '.')
                            
                            # Convert to appropriate numeric type
                            try:
                                if clean_val.replace('.', '').isdigit() or (clean_val.startswith('-') and clean_val[1:].replace('.', '').isdigit()):
                                    if isinstance(field, models.DecimalField):
                                        dados[campo] = Decimal(clean_val)
                                    elif isinstance(field, models.FloatField):
                                        dados[campo] = float(clean_val)
                                    elif isinstance(field, models.IntegerField):
                                        dados[campo] = int(round(float(clean_val)))
                                else:
                                    dados[campo] = None
                            except (ValueError, TypeError, InvalidOperation):
                                dados[campo] = None
                        else:
                            # For CharField and other non-numeric fields, keep as is
                            dados[campo] = valor
                    except (ValueError, TypeError):
                        # If conversion fails, set to None for numeric fields, keep as is for others
                        if isinstance(field, (models.DecimalField, models.FloatField, models.IntegerField)):
                            dados[campo] = None
                        else:
                            dados[campo] = valor
            

            Acoes.objects.update_or_create(
                papel=papel,
                defaults=dados
            )
            
        except Exception as e:
            print(f"Erro ao processar {papel}: {str(e)}")

def run_scraper():

    process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR'})
    spider = AcaoSpider()
    process.crawl(AcaoSpider)
    process.start()
    

    if not (hasattr(spider, 'dados_kpi') and spider.dados_kpi):
        print("Nenhum dado foi coletado para salvar.")
        return

    df1 = pd.DataFrame(spider.dados_kpi).fillna("")
    df2 = pd.DataFrame(spider.dados_indicadores).fillna("")
    df3 = pd.DataFrame(spider.dados_info).fillna("")
    df4 = pd.DataFrame(spider.dados_img).fillna("")
    
    df = pd.merge(df1, df2).merge(df3).merge(df4)
    
    if not df.empty:
        if 'P/L' in df.columns:
            df['P/L'] = df['P/L'].apply(remover_segundo_ponto)
        if 'PAYOUT' in df.columns:
            df['PAYOUT'] = df['PAYOUT'].apply(remover_segundo_ponto)
        if 'ROE' in df.columns:
            df['ROE'] = df['ROE'].apply(remover_segundo_ponto)
        if 'carteira_investidor_10' in df.columns:
            df = df.drop(columns=["carteira_investidor_10"])
        
        df = df.applymap(lambda x: "" if x == "-" else x)
    

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

    if not df.empty:
        output_file = "acoes.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Dados salvos em {output_file}")
    else:
        print("Nenhum dado disponível para salvar.")

def remover_segundo_ponto(val):
    if pd.isna(val):
        return val
    val = str(val).strip()
    val = val.replace(',', '.')        
    partes = val.split('.')           
    if len(partes) > 2:
        return '.'.join(partes[:-1]) + partes[-1]
    return val

if __name__ == "__main__":
    run_scraper()
