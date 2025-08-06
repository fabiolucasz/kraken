from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import Acoes, UserFavoriteAcoes
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def rank_acoes(filters=None):
    # Buscar dados do banco de dados
    queryset = Acoes.objects.all()
    
    # Aplicar filtros se existirem
    if filters:
        # ROE
        if 'roe_min' in filters:
            try:
                min_roe = float(filters['roe_min'])
                queryset = queryset.filter(roe__gte=min_roe)
            except ValueError:
                pass
        
        # CAGR
        if 'cagr_min' in filters:
            try:
                min_cagr = float(filters['cagr_min'])
                queryset = queryset.filter(cagr_lucros_5_anos__gte=min_cagr)
            except ValueError:
                pass
        
        # P/L
        if 'pl_min' in filters:
            try:
                min_pl = float(filters['pl_min'])
                queryset = queryset.filter(pl__gte=min_pl)
            except ValueError:
                pass
        
        # Margem Líquida
        if 'margem_liquida_min' in filters:
            try:
                min_margem = float(filters['margem_liquida_min'])
                queryset = queryset.filter(margem_liquida__gte=min_margem)
            except ValueError:
                pass
        
        # Setor
        if 'Setor' in filters:
            setor = filters['Setor'].strip()
            if setor:
                queryset = queryset.filter(setor__icontains=setor)
        
        # Segmento
        if 'Segmento' in filters:
            segmento = filters['Segmento'].strip()
            if segmento:
                queryset = queryset.filter(segmento__icontains=segmento)
    
    # Converter para DataFrame
    df = pd.DataFrame(list(queryset.values(
        'id',
        'papel',
        'cotation',
        'pl',
        'pv',
        'dy',
        'payout',
        'roe',
        'margem_liquida',
        'cagr_lucros_5_anos',
        'ticker_img',
        'setor',
        'segmento',
    )))
    
    # Renomear colunas para o formato esperado
    df = df.rename(columns={
        'papel': 'Papel',
        'cotation': 'Cotação',
        'pl': 'P/L',
        'pv': 'P/VP',
        'dy': 'DY',
        'roe': 'ROE',
        'payout': 'PAYOUT',
        'margem_liquida': 'MARGEM_LÍQUIDA',
        'cagr_lucros_5_anos': 'CAGR_LUCROS_5_ANOS',
        'ticker_img': 'Ticker_Img',
        'setor': 'Setor',
        'segmento': 'Segmento',
    })
    
    # Calcular ranking ponderado
    indicadores = {
        'DY': 1,
        'P/L': 1,
        'PAYOUT': 1,
        'P/VP': -1,
        'ROE': 1,
        'CAGR_LUCROS_5_ANOS': 1,
        'MARGEM_LÍQUIDA': 1
    }
    
    scaler = MinMaxScaler()
    
    for col, peso in indicadores.items():
        # Normalizar entre 0 e 1
        norm = scaler.fit_transform(df[[col]].fillna(0))  # Preencher NaN com 0
        if peso < 0:
            norm = 1 - norm  # inverter se menor é melhor
        df[f'{col}_score'] = norm * abs(peso)
    
    df['Rank_ponderado'] = df[[f'{col}_score' for col in indicadores]].sum(axis=1)
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    
    # Adicionar coluna de rank
    df['Rank'] = range(1, len(df) + 1)
    
    # Manter apenas as colunas necessárias
    df = df[['Rank', 'Papel', 'Cotação', 'P/L', 'DY', 'P/VP', 'ROE', 'PAYOUT', 'MARGEM_LÍQUIDA', 'CAGR_LUCROS_5_ANOS', 'Ticker_Img', 'Setor', 'Segmento']]
    
    return df

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
    
    # Obter valores únicos de setores e segmentos
    setores_unicos = df['Setor'].unique().tolist()
    segmentos_unicos = df['Segmento'].unique().tolist()
    
    # Converter DataFrame para lista de dicionários compatível com o template
    data = []
    
    # Adicionar status de favorito para cada Ação se o usuário estiver logado
    if request.user.is_authenticated:
        favorites = UserFavoriteAcoes.objects.filter(user=request.user)
        favorite_dict = {fav.acoes.papel: fav.is_favorite for fav in favorites}
    
    for index, row in df.iterrows():
        row_data = {}
        
        # Primeiro, garantimos que temos o papel
        papel = str(row['Papel']) if 'Papel' in df.columns else str(row['papel'])
        row_data['Papel'] = papel
        
        # Adicionamos o status de favorito
        if request.user.is_authenticated:
            row_data['is_favorite'] = favorite_dict.get(papel, False)
        
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
        row_data['CAGR_LUCROS_5_ANOS'] = row['CAGR_LUCROS_5_ANOS']
        row_data['Ticker_Img'] = row['Ticker_Img']
        row_data['Setor'] = row['Setor']
        row_data['Segmento'] = row['Segmento']
        
        data.append(row_data)
    
    return render(request, 'acoes/index.html', {
        'data': data,
        'filters': filters,
        'setores': setores_unicos,
        'segmentos': segmentos_unicos,
    })

def acao(request, papel):
    acoes = get_object_or_404(Acoes, papel=papel)
    return render(request, 'acoes/acao.html', {'acoes': acoes})
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