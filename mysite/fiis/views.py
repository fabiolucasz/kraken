from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import Fiis, UserFavoriteFiis
from django.contrib import messages
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def rank_fiis(filters=None):
    queryset = Fiis.objects.all()
    
    # filtro prévio com os nomes corretos dos campos
    queryset = queryset.filter(dividend_yield__gte=6)
    queryset = queryset.filter(liquidez_diaria_rs__gte=500000)
    queryset = queryset.filter(pvp__gte=0.75)
    queryset = queryset.filter(vacancia__lte=30)

    if filters:
        # DY
        if 'dy_min' in filters:
            try:
                min_dy = float(filters['dy_min'])
                queryset = queryset.filter(dividend_yield__gte=min_dy)
            except ValueError:
                pass

        # Liquidez
        if 'liquidez_min' in filters:
            try:
                min_liquidez = float(filters['liquidez_min'])
                queryset = queryset.filter(liquidez_diaria_rs__gte=min_liquidez)
            except ValueError:
                pass

        # PVP
        if 'pvp_min' in filters:
            try:
                min_pvp = float(filters['pvp_min'])
                queryset = queryset.filter(pvp__lte=min_pvp)
            except ValueError:
                pass

        if 'pvp_max' in filters:
            try:
                max_pvp = float(filters['pvp_max'])
                queryset = queryset.filter(pvp__lte=max_pvp)
            except ValueError:
                pass

        if 'vacancia_max' in filters:
            try:
                max_vacancia = float(filters['vacancia_max'])
                queryset = queryset.filter(vacancia__lte=max_vacancia)
            except ValueError:
                pass
        
        
        if 'setor' in filters:
            try:
                queryset = queryset.filter(setor__icontains=filters['setor'])
            except ValueError:
                pass

    df = pd.DataFrame(list(queryset.values(
        'id',
        'dividend_yield',
        'liquidez_diaria_rs',
        'papel',
        'cotacao',
        'pvp',
        'setor',
        'ultimo_dividendo',
        'vacancia',
    )))


    # Indicadores relevantes
    indicadores = {
        'dy': 1,  # quanto maior, melhor
        'liquidez_diaria_rs': 0.5,  # quanto maior, melhor
        'pvp': -0.5,  # quanto menor, melhor
        'vacancia': -0.5,  # quanto menor, melhor
    }

   

    # Normalizar os dados
    scaler = MinMaxScaler()

    for col, peso in indicadores.items():
        # Normalizar entre 0 e 1
        norm = scaler.fit_transform(df[[col]].fillna(0))
        if peso < 0:
            norm = 1 - norm  # inverter se menor é melhor
        df[f'{col}_score'] = norm * abs(peso)

    # Rank final como soma ponderada dos score
    df['Rank_ponderado'] = df[[f'{col}_score' for col in indicadores]].sum(axis=1)
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    df['Rank'] = range(1, len(df) + 1)

    # Organizando as colunas finais
    ordered_df = df[['Rank', 'papel', 'cotacao', 'dividend_yield', 'pvp', 'liquidez_diaria_rs', 'vacancia']]
    df = ordered_df

    return df

# Comentado para evitar execução durante a importação
# rank_fiis(filters=None)

def index(request):
    # Se for POST, salvamos os filtros no cache
    if request.method == 'POST':
        filters = request.POST.dict()
        cache_key = f"fiis_filters_{request.session.session_key}"
        cache.set(cache_key, filters, 3600)  # Cache por 1 hora
    else:
        # Se não for POST, recuperamos os filtros do cache
        cache_key = f"fiis_filters_{request.session.session_key}"
        filters = cache.get(cache_key, {})
      
    # Obtém os dados dos FIIs
    df = rank_fiis(filters=filters)

    # Obtém setores únicos para o filtro
    segmentos_unicos = sorted(df['setor'].dropna().unique().tolist()) if 'setor' in df.columns else []
    
    # Prepara os dados para o template
    data = []

    # Adicionar status de favorito para cada Ação se o usuário estiver logado
    if request.user.is_authenticated:
        favorites = UserFavoriteFiis.objects.filter(user=request.user)
        favorite_dict = {fav.fiis.papel: fav.is_favorite for fav in favorites}

    for index, row in df.iterrows():
        row_data = {}
        
        # Primeiro, garantimos que temos o papel
        papel = str(row['papel']) if 'papel' in df.columns else str(row['papel'])
        row_data['papel'] = papel
        
        # Adicionamos o status de favorito
        if request.user.is_authenticated:
            row_data['is_favorite'] = favorite_dict.get(papel, False)
        
        # Adicionamos o rank
        row_data['Rank'] = row['Rank']
        row_data['cotacao'] = row['cotacao']
        row_data['dy'] = row['dy']
        row_data['pvp'] = row['pvp']
        row_data['liquidez_diaria_rs'] = row['liquidez_diaria_rs']
        row_data['dividend_yield'] = row['dividend_yield']
        row_data['vacancia'] = row['vacancia']            
        data.append(row_data)

    return render(request, 'fiis/index.html', {
        'data': data,
        'filters': filters,
        'setores': segmentos_unicos,
        'total_fiis': len(data),
    })
   

def fii(request, papel):
    fiis = get_object_or_404(Fiis, papel=papel)
    return render(request, 'fiis/fii.html', {'fiis': fiis})
@login_required
def toggle_favorite(request, papel):
    fiis = get_object_or_404(Fiis, papel=papel)
    favorite, created = UserFavoriteFiis.objects.get_or_create(
        user=request.user,
        fiis=fiis
    )
   
    # Altera o estado de favorito
    favorite.is_favorite = not favorite.is_favorite
    favorite.save()
   
    # Adiciona mensagem de feedback
    if favorite.is_favorite:
        messages.success(request, f'FII {papel} adicionado aos favoritos!')
    else:
        messages.success(request, f'FII {papel} removido dos favoritos!')
   
    # Redireciona de volta para a página principal
    return redirect('fiis:index')