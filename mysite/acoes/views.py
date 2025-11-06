from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from .client import KrakenAPIClient
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def rank_acoes(filters=None):
    api_client = KrakenAPIClient()
    try:
        # Busca dados da API
        acoes_ranking = api_client.get_acoes_ranking()
        df = pd.DataFrame(acoes_ranking)
        
        # Se não houver dados, retorna DataFrame vazio
        if df.empty:
            return df

        # Renomear colunas para manter compatibilidade
        col_rename = {
            'cotacao_atual': 'Cotação',
            'p_l': 'P/L',
            'dy': 'DY',
            'p_vp': 'P/VP',
            'payout': 'PAYOUT',
            'roe': 'ROE',
            'margem_líquida': 'MARGEM_LÍQUIDA',
            'ticker_img': 'Ticker_Img',
            'setor': 'Setor',
            'segmento': 'Segmento'
        }
        
        # Aplicar renomeação apenas para colunas que existem no DataFrame
        df = df.rename(columns={k: v for k, v in col_rename.items() if k in df.columns})
            
        # Aplicar filtros
        # if filters:
        #     # Filtro por setor
        #     if 'setor' in filters and filters['setor']:
        #         df = df[df['Setor'].str.contains(filters['setor'], case=False, na=False)]
                
        #     # Filtro por DY mínimo
        #     if 'dy_min' in filters and filters['dy_min']:
        #         try:
        #             min_dy = float(filters['dy_min'])
        #             df = df[df['DY'] >= min_dy]
        #         except (ValueError, TypeError):
        #             pass

        # Cálculo do ranking
        indicadores = {
            'DY': 1,           # Quanto maior, melhor
            'P/L': -1,         # Quanto menor, melhor (invertido)
            'PAYOUT': 1,       # Quanto maior, melhor
            'P/VP': -1,        # Quanto menor, melhor (invertido)
            'ROE': 1,          # Quanto maior, melhor
            'MARGEM_LÍQUIDA': 1 # Quanto maior, melhor
        }

        # Filtrar apenas indicadores que existem no DataFrame
        indicadores = {k: v for k, v in indicadores.items() if k in df.columns}
        
        # Normalização dos dados
        if indicadores:  # Só faz se houver indicadores para processar
            scaler = MinMaxScaler()

            for col, peso in indicadores.items():
                # Preencher valores nulos com a mediana
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median())
                
                # Normalizar entre 0 e 1
                norm = scaler.fit_transform(df[[col]])
                if peso < 0:
                    norm = 1 - norm  # inverter se menor é melhor
                df[f'{col}_score'] = norm * abs(peso)

            # Calcular score final
            score_columns = [f'{col}_score' for col in indicadores]
            df['Rank_ponderado'] = df[score_columns].sum(axis=1)
            df = df.sort_values(by='Rank_ponderado', ascending=False)
        
        # Adicionar coluna de rank
        df['Rank'] = range(1, len(df) + 1)

        # Selecionar e ordenar colunas
        colunas_retorno = [
            'Rank', 'papel', 'Cotação', 'P/L', 'DY', 'P/VP', 
            'ROE', 'PAYOUT', 'MARGEM_LÍQUIDA', 'Ticker_Img', 'Setor', 'Segmento'
        ]
        
        # Garantir que as colunas existam no DataFrame
        colunas_disponiveis = [col for col in colunas_retorno if col in df.columns]
        df = df[colunas_disponiveis]
        
        return df
        
    except Exception as e:
        print(f"Erro ao processar ranking de ações: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

def index(request):
    # Se for POST, salvamos os filtros no cache
    if request.method == 'POST':
        filters = request.POST.dict()
        cache_key = f"acoes_filters_{request.session.session_key}"
        cache.set(cache_key, filters, 3600)  # Cache por 1 hora
    else:
        # Se não for POST, recuperamos os filtros do cache
        cache_key = f"acoes_filters_{request.session.session_key}"
        filters = cache.get(cache_key, {})

    # Obter os dados e aplicar filtros diretamente no banco
    df = rank_acoes(filters=filters)
    print(f"Dados retornados: {df}")
    
    # Obter valores únicos de setores e segmentos
    # setores_unicos = df['Setor'].unique().tolist()
    # segmentos_unicos = df['Segmento'].unique().tolist()
    
    # Converter DataFrame para lista de dicionários compatível com o template
    data = []
    
    # Adicionar status de favorito para cada Ação se o usuário estiver logado
    # if request.user.is_authenticated:
    #     favorites = UserFavoriteAcoes.objects.filter(user=request.user)
    #     favorite_dict = {fav.acoes.papel: fav.is_favorite for fav in favorites}
    
    for index, row in df.iterrows():
        row_data = {}
        
        # Primeiro, garantimos que temos o papel
        papel = str(row['papel']) if 'papel' in df.columns else str(row['papel'])
        row_data['papel'] = papel
        
        # Adicionamos o status de favorito
        # if request.user.is_authenticated:
        #     row_data['is_favorite'] = favorite_dict.get(papel, False)
        
        # Adicionamos o rank
        row_data['Rank'] = row['Rank']
        
        # Adicionamos os outros campos
        row_data['Cotação'] = row['Cotação']
        row_data['PL'] = row['P/L']
        row_data['DY'] = row['DY']
        row_data['PVP'] = row['P/VP']
        row_data['ROE'] = row['ROE']
        row_data['PAYOUT'] = row['PAYOUT']
        row_data['MARGEM_LÍQUIDA'] = row['MARGEM_LÍQUIDA']
        row_data['Ticker_Img'] = row['Ticker_Img']
        row_data['Setor'] = row['Setor']
        row_data['Segmento'] = row['Segmento']
        
        data.append(row_data)
    
    return render(request, 'acoes/index.html', {
        'data': data,
        'filters': filters,
        # 'setores': setores_unicos,
        # 'segmentos': segmentos_unicos,
    })

@login_required
def toggle_favorite(request, papel):
    acoes = get_object_or_404(Acoes, papel=papel)
    favorite, created = UserFavoriteAcoes.objects.get_or_create(
        user=request.user,
        acoes=acoes
    )
   
    # Altera o estado de favorito
    favorite.is_favorite = not favorite.is_favorite
    favorite.save()
   
    # Adiciona mensagem de feedback
    if favorite.is_favorite:
        messages.success(request, f'Ação {papel} adicionada aos favoritos!')
    else:
        messages.success(request, f'Ação {papel} removida dos favoritos!')
   
    # Redireciona de volta para a página principal
    return redirect('acoes:index')

# acoes/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from .client import KrakenAPIClient

def test_api_view(request):
    """View para testar o consumo da API de ações"""
    try:
        # Inicializa o cliente da API
        api_client = KrakenAPIClient()
        
        # Faz a requisição para a API
        acoes = api_client.get_acoes_ranking()
        
        # Pega apenas as 5 primeiras para o teste
        primeiras_acoes = acoes[:5] if len(acoes) > 5 else acoes
        
        # Se estiver em ambiente de desenvolvimento, mostra os dados no template
        if settings.DEBUG:
            context = {
                'status': 'success',
                'count': len(primeiras_acoes),
                'data': primeiras_acoes,
                'raw_data': json.dumps(primeiras_acoes, indent=2, ensure_ascii=False)
            }
            return render(request, 'acoes/test_api.html', context)
        
        # Em produção, retorna apenas JSON
        return JsonResponse({
            'status': 'success',
            'count': len(primeiras_acoes),
            'data': primeiras_acoes
        })
        
    except Exception as e:
        error_message = f"Erro ao acessar a API: {str(e)}"
        if settings.DEBUG:
            return render(request, 'acoes/test_api.html', {
                'status': 'error',
                'message': error_message
            }, status=500)
        return JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=500)