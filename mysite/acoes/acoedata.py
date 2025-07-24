import pandas as pd
from .models import Acoes

def import_acoes_from_csv():
    try:
        # Carrega o arquivo CSV
        df = pd.read_csv('./../acoes.csv')
        
        # Itera sobre cada linha do DataFrame
        for _, row in df.iterrows():
            papel = row['Papel']
            
            # Verifica se o papel já existe no banco de dados
            if not Acoes.objects.filter(papel=papel).exists():
                # Cria um novo registro
                acao = Acoes(
                    papel=papel
                )
                acao.save()
        
        return True
    except Exception as e:
        print(f"Erro ao importar dados: {str(e)}")
        return False
