import os
import sys
import django
import pandas as pd
from decimal import Decimal, InvalidOperation

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from acoes.models import Acoes


def importar_dados():
    print("Iniciando importação de dados...")
    
    # Mapeamento dos campos do CSV para o modelo
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

    # Campos que são decimais
    decimal_fields = [
        'cotation', 'variation_12m', 'pl', 'pv', 'dy', 'psr', 'payout',
        'margem_liquida', 'margem_bruta', 'margem_ebit', 'margem_ebitda',
        'ev_ebitda', 'ev_ebit', 'pebitda', 'pebit', 'pativo', 'p_cap_giro',
        'p_ativo_circ_liq', 'vpa', 'lpa', 'giro_ativos', 'roe', 'roic', 'roa',
        'divida_liquida_patrimonio', 'divida_liquida_ebitda', 'divida_liquida_ebit',
        'divida_bruta_patrimonio', 'patrimonio_ativos', 'passivos_ativos',
        'liquidez_corrente', 'cagr_receitas_5_anos', 'cagr_lucros_5_anos',
        'free_float','tag_along'
    ]

    # Campos que são BigInteger
    biginteger_fields = [
        'valor_mercado', 'valor_firma', 'patrimonio_liquido', 'numero_papeis',
        'ativos', 'ativo_circulante', 'divida_bruta', 'divida_liquida',
        'disponibilidade'
    ]

    # Campos que são texto
    text_fields = [
        'segmento_listagem', 'setor', 'segmento', 'ticker_img'
    ]

    print(f"Lendo arquivo CSV: acoes.csv")
    
    # Carrega o CSV com conversão de tipos
    df = pd.read_csv('acoes.csv', encoding='utf-8', dtype=str)
    print(f"CSV carregado com {len(df)} linhas")
    
    print(f"CSV carregado com {len(df)} linhas")
    print("Colunas do CSV:")
    for col in df.columns:
        print(f"- {col}")

    # Processa cada linha do CSV
    for index, row in df.iterrows():
        papel = str(row['Papel']).strip()
        print(f"\nProcessando registro para {papel}")
        
        # Cria um dicionário temporário para armazenar os valores
        dados = {'papel': papel}
        
        # Processa cada campo
        for col in df.columns:
            if col != 'Papel':
                campo = campos_map.get(col)
                if campo:
                    valor = row[col]
                    try:
                        # Tratamento especial para campos decimais
                        if campo in decimal_fields:
                            try:
                                if pd.notna(valor):
                                    valor = str(valor).strip()
                                    if valor:
                                        # Remove caracteres especiais
                                        valor = valor.replace('%', '').replace('$', '').replace('"', '').strip()
                                        # Remove separador de milhar (ponto)
                                        valor = valor.replace('.', '', valor.count('.') - 1)
                                        # Substitui vírgula por ponto
                                        valor = valor.replace(',', '.')
                                        
                                        try:
                                            # Tenta converter para decimal
                                            decimal_value = Decimal(valor)
                                            # Se o valor está fora do range aceitável para decimal, seta como None
                                            if abs(decimal_value) > 1000000000:  # Limite arbitrário para valores muito grandes
                                                print(f"Valor muito grande para decimal em {campo}: {valor}")
                                                dados[campo] = None
                                            else:
                                                dados[campo] = decimal_value
                                        except InvalidOperation:
                                            try:
                                                # Tenta converter para float primeiro
                                                float_value = float(valor)
                                                dados[campo] = Decimal(str(float_value))
                                            except (ValueError, TypeError):
                                                print(f"Erro de conversão para decimal em {campo}: {valor}")
                                                dados[campo] = None
                                    else:
                                        dados[campo] = None
                                else:
                                    dados[campo] = None
                            except Exception as e:
                                print(f"Erro ao processar decimal {campo}: {str(e)}")
                                dados[campo] = None
                        # Tratamento especial para campos BigInteger
                        elif campo in biginteger_fields:
                            try:
                                if pd.notna(valor):
                                    valor = str(valor).strip()
                                    if valor:
                                        # Remove caracteres especiais
                                        valor = valor.replace('%', '').replace('$', '').replace('"', '').strip()
                                        # Remove separador de milhar (ponto)
                                        valor = valor.replace('.', '')
                                        # Remove separador decimal (vírgula)
                                        valor = valor.replace(',', '')
                                        
                                        try:
                                            # Tenta converter para int
                                            int_value = int(valor)
                                            # Se o valor está fora do range aceitável para BigInteger, seta como None
                                            if abs(int_value) > 9223372036854775807:  # Limite do BigInteger
                                                print(f"Valor muito grande para BigInteger em {campo}: {valor}")
                                                dados[campo] = None
                                            else:
                                                dados[campo] = int_value
                                        except ValueError:
                                            try:
                                                # Tenta converter para float primeiro
                                                float_value = float(valor)
                                                dados[campo] = int(float_value)
                                            except (ValueError, TypeError):
                                                print(f"Erro de conversão para BigInteger em {campo}: {valor}")
                                                dados[campo] = None
                                    else:
                                        dados[campo] = None
                                else:
                                    dados[campo] = None
                            except Exception as e:
                                print(f"Erro ao processar BigInteger {campo}: {str(e)}")
                                dados[campo] = None
                        # Tratamento para campos de texto
                        elif campo in text_fields:
                            try:
                                if pd.notna(valor):
                                    valor = str(valor).strip()
                                    if valor:
                                        # Remove aspas se existirem
                                        valor = valor.strip('"')
                                        dados[campo] = valor
                                    else:
                                        dados[campo] = None
                                else:
                                    dados[campo] = None
                            except Exception:
                                dados[campo] = None
                    except Exception:
                        dados[campo] = None
        
        # Atualiza ou cria o registro
        try:
            # Prepara os dados para salvar
            dados_salvar = {'papel': papel}
            
            # Adiciona campos decimais
            for campo in decimal_fields:
                if campo in dados and dados[campo] is not None:
                    try:
                        valor = str(dados[campo]).strip()
                        if valor:
                            # Remove caracteres especiais
                            valor = valor.replace('%', '').replace('$', '').replace('"', '').strip()
                            
                            # Se o valor é uma string vazia, '-', 'não disponível', 'não há dados', ou 'N/A', seta como None
                            if valor == '' or valor == '-' or 'não disponível' in valor.lower() or 'não há dados' in valor.lower() or valor.lower() == 'n/a':
                                # Para o campo variation_12m, seta como 0 ao invés de None
                                if campo == 'variation_12m':
                                    print(f"Valor especial para {campo}: {valor} - setando como 0")
                                    dados_salvar[campo] = Decimal('0')
                                    continue
                                
                                print(f"Valor inválido para decimal em {campo}: {valor}")
                                dados_salvar[campo] = None
                                continue
                            
                            # Remove caracteres extras que podem aparecer
                            valor = valor.replace('R$', '').replace('BRL', '').strip()
                            
                            # Tratamento especial para valores entre parênteses
                            if '(' in valor and ')' in valor:
                                # Remove os parênteses e marca como negativo
                                valor = valor.replace('(', '').replace(')', '').strip()
                                negativo = True
                            else:
                                negativo = valor.startswith('-')
                                valor = valor.lstrip('-').strip()
                            
                            # Remove múltiplos pontos e vírgulas
                            # Mantém apenas o último ponto ou vírgula como separador decimal
                            pontos = valor.count('.')
                            virgulas = valor.count(',')
                            
                            if pontos > 1 or virgulas > 1:
                                # Para campos de dívida e disponibilidade, seta como 0 se tiver múltiplos separadores
                                if campo in ['divida_bruta', 'divida_liquida', 'disponibilidade']:
                                    print(f"Valor com múltiplos separadores para {campo}: {valor} - setando como 0")
                                    dados_salvar[campo] = 0
                                    continue
                                
                                # Para outros campos, mantém apenas o último separador
                                if pontos > 0 and virgulas > 0:
                                    valor = valor.replace('.', '').replace(',', '').strip()
                                elif pontos > 0:
                                    valor = valor.replace('.', '', pontos - 1)
                                elif virgulas > 0:
                                    valor = valor.replace(',', '', virgulas - 1)
                            
                            # Substitui vírgula por ponto
                            valor = valor.replace(',', '.')
                            
                            # Remove espaços extras
                            valor = valor.strip()
                            
                            try:
                                # Tenta converter para decimal
                                decimal_value = Decimal(valor)
                                if negativo:
                                    decimal_value = -decimal_value
                                # Se o valor está fora do range aceitável para decimal, seta como None
                                if abs(decimal_value) > 1000000000:  # Limite arbitrário para valores muito grandes
                                    print(f"Valor muito grande para decimal em {campo}: {valor}")
                                    dados_salvar[campo] = None
                                else:
                                    dados_salvar[campo] = decimal_value
                            except InvalidOperation:
                                try:
                                    # Tenta converter para float primeiro
                                    float_value = float(valor)
                                    if negativo:
                                        float_value = -float_value
                                    dados_salvar[campo] = Decimal(str(float_value))
                                except (ValueError, TypeError):
                                    print(f"Erro convertendo {campo} para decimal: {valor}")
                                    dados_salvar[campo] = None
                        else:
                            dados_salvar[campo] = None
                    except Exception as e:
                        print(f"Erro ao processar decimal {campo}: {str(e)}")
                        dados_salvar[campo] = None
            
            # Adiciona campos BigInteger
            for campo in biginteger_fields:
                if campo in dados and dados[campo] is not None:
                    try:
                        valor = str(dados[campo]).strip()
                        if valor:
                            # Remove caracteres especiais
                            valor = valor.replace('%', '').replace('$', '').replace('"', '').strip()
                            
                            # Se o valor é uma string vazia, '-', 'não disponível', 'não há dados', ou 'N/A', seta como None
                            if valor == '' or valor == '-' or 'não disponível' in valor.lower() or 'não há dados' in valor.lower() or valor.lower() == 'n/a':
                                # Para campos específicos, seta como 0 ao invés de None
                                if campo in ['divida_bruta', 'divida_liquida', 'disponibilidade']:
                                    print(f"Valor especial para {campo}: {valor} - setando como 0")
                                    dados_salvar[campo] = 0
                                    continue
                                
                                print(f"Valor inválido para BigInteger em {campo}: {valor}")
                                dados_salvar[campo] = None
                                continue
                            
                            # Se o valor é um número muito pequeno (menor que 1), seta como 0
                            try:
                                num = float(valor)
                                if abs(num) < 1:
                                    print(f"Valor muito pequeno para {campo}: {valor} - setando como 0")
                                    dados_salvar[campo] = 0
                                    continue
                            except ValueError:
                                pass
                            
                            # Tratamento especial para valores entre parênteses
                            if '(' in valor and ')' in valor:
                                # Remove os parênteses e marca como negativo
                                valor = valor.replace('(', '').replace(')', '').strip()
                                negativo = True
                            else:
                                negativo = valor.startswith('-')
                                valor = valor.lstrip('-').strip()
                            
                            # Remove caracteres extras que podem aparecer
                            valor = valor.replace('R$', '').replace('BRL', '').strip()
                            
                            # Remove múltiplos pontos e vírgulas
                            # Mantém apenas o último ponto ou vírgula como separador decimal
                            if '.' in valor and ',' in valor:
                                # Mantém apenas o último ponto ou vírgula
                                valor = valor.replace('.', '').replace(',', '').strip()
                            elif '.' in valor:
                                # Remove todos os pontos exceto o último
                                valor = valor.replace('.', '', valor.count('.') - 1)
                            elif ',' in valor:
                                # Remove todas as vírgulas exceto a última
                                valor = valor.replace(',', '', valor.count(',') - 1)
                            
                            # Remove espaços extras
                            valor = valor.strip()
                            
                            try:
                                # Tenta converter para int
                                int_value = int(valor)
                                if negativo:
                                    int_value = -int_value
                                # Se o valor está fora do range aceitável para BigInteger, seta como None
                                if abs(int_value) > 9223372036854775807:  # Limite do BigInteger
                                    print(f"Valor muito grande para BigInteger em {campo}: {valor}")
                                    dados_salvar[campo] = None
                                else:
                                    dados_salvar[campo] = int_value
                            except ValueError:
                                try:
                                    # Tenta converter para float primeiro
                                    float_value = float(valor)
                                    if negativo:
                                        float_value = -float_value
                                    int_value = int(float_value)
                                    if abs(int_value) > 9223372036854775807:
                                        print(f"Valor muito grande para BigInteger em {campo}: {valor}")
                                        dados_salvar[campo] = None
                                    else:
                                        dados_salvar[campo] = int_value
                                except (ValueError, TypeError):
                                    print(f"Erro convertendo {campo} para int: {valor}")
                                    dados_salvar[campo] = None
                        else:
                            dados_salvar[campo] = None
                    except Exception as e:
                        print(f"Erro ao processar BigInteger {campo}: {str(e)}")
                        dados_salvar[campo] = None
            
            # Adiciona campos texto
            for campo in text_fields:
                if campo in dados and dados[campo] is not None:
                    dados_salvar[campo] = str(dados[campo])
            
            # Atualiza o registro existente
            try:
                acao = Acoes.objects.get(papel=papel)
                # Atualiza apenas os campos que não são papel ou id
                for campo in dados_salvar:
                    if campo not in ['papel', 'id']:
                        setattr(acao, campo, dados_salvar[campo])
                acao.save()
                print(f"Atualizado registro para {papel}")
            except Exception as e:
                print(f"Erro ao salvar registro {papel}: {str(e)}")
                print(f"Dados: {dados_salvar}")
                continue
        except Exception as e:
            print(f"Erro ao processar registro {papel}: {str(e)}")
            print(f"Dados: {dados}")
            continue
    
    print("Importação concluída!")

if __name__ == '__main__':
    # Executar o scraper no diretório correto
    # os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # from scraper.spiders.acao_spider import run_scraper
    # run_scraper()
    importar_dados()