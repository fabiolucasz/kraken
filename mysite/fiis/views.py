from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import Fiis, UserFavoriteFiis
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def rank_fiis():
    df = pd.read_csv("./../fundos_imobiliarios.csv", quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    df = df.rename(columns={
        "Fundos": "Papel",
        "Preço Atual (R$)": "Cotação",
        "DY (12M) Acumulado": "DY",
        "Liquidez Diária (R$)": "Liquidez",
    })

    #filtro prévio
    df = df[df['DY'] > 6]
    df = df[df['Liquidez'] > 500000]
    df = df[df['P/VP'] >= 0.75]

    # Indicadores relevantes
    indicadores = {
        'DY': 1,  # quanto maior, melhor
        'Liquidez': 0.5,  # quanto maior, melhor
        'P/VP': -0.5  # quanto menor, melhor
    }

    # Normalizar os dados
    scaler = MinMaxScaler()

    for col, peso in indicadores.items():
        # Normalizar entre 0 e 1
        norm = scaler.fit_transform(df[[col]])
        if peso < 0:
            norm = 1 - norm  # inverter se menor é melhor
        df[f'{col}_score'] = norm * abs(peso)

    # Rank final como soma ponderada dos scores
    df['Rank_ponderado'] = df[[f'{col}_score' for col in indicadores]].sum(axis=1)

    # Converter colunas para numérico, forçando erros para NaN
    df['Último Dividendo'] = pd.to_numeric(df['Último Dividendo'], errors='coerce')
    df['Cotação'] = pd.to_numeric(df['Cotação'], errors='coerce')
    df['DY'] = pd.to_numeric(df['DY'], errors='coerce')

    # Calcular o DY/mês e YOC
    df['DY/mês'] = ((df['Último Dividendo'] / df['Cotação']) * 100).round(2)
    df['YOC'] = ((df['DY'] / df['Cotação']) * 100).round(2)

    # Ordenar
    df.drop(columns=['P/VP_score', 'DY_score', 'Liquidez_score'])
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    # Organizando as colunas finais
    ordered_df = df[['Rank', 'Papel', 'Setor', 'Cotação', 'DY', 'P/VP', 'Liquidez', 'Dividend Yield']]
    df = ordered_df

    return df

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

    # Carregamos o DataFrame
    df = rank_fiis()
    segmentos_unicos = df['Setor'].dropna().unique()

    # Aplicamos os filtros
    if filters:
        # Dividend Yield
        if 'dividend_yield_min' in filters:
            try:
                min_yield = float(filters['dividend_yield_min'])
                df = df[df['DY'] >= min_yield]
            except ValueError:
                pass
       
        # Liquidez
        if 'liquidez_min' in filters:
            try:
                min_liquidez = float(filters['liquidez_min'])
                df = df[df['Liquidez'] >= min_liquidez]
            except ValueError:
                pass
       
        # PVP
        if 'pvp_min' in filters:
            try:
                min_pvp = float(filters['pvp_min'])
                df = df[df['P/VP'] >= min_pvp]
            except ValueError:
                pass
       
        if 'pvp_max' in filters:
            try:
                max_pvp = float(filters['pvp_max'])
                df = df[df['P/VP'] <= max_pvp]
            except ValueError:
                pass
       
        # Segmento
        if 'Setor' in filters:
            segmento = filters['Setor'].strip()
            if segmento:
                df = df[df['Setor'].str.contains(segmento, case=False, na=False)]

    # Recalcular o ranking após os filtros
    df = df.reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)
    df = df.sort_values('Rank')

    # Preparar os dados para o template
    data = []
    columns = df.columns.tolist()
   
    # Adicionar status de favorito para cada FII se o usuário estiver logado
    if request.user.is_authenticated:
        favorites = UserFavoriteFiis.objects.filter(user=request.user)
        favorite_dict = {fav.fiis.papel: fav.is_favorite for fav in favorites}
   
    # Converter DataFrame para lista de dicionários compatível com o template
    for index, row in df.iterrows():
        row_data = {}
       
        # Primeiro, garantimos que temos o papel
        papel = str(row['Papel']) if 'Papel' in df.columns else str(row['papel'])
        row_data['Papel'] = papel
       
        # Adicionamos o status de favorito
        if request.user.is_authenticated:
            row_data['is_favorite'] = favorite_dict.get(papel, False)
       
        # Adicionamos os outros campos, garantindo que os nomes sejam compatíveis com o template
        for col in columns:
            if col != 'Papel':  # Já adicionamos o Papel acima
                # Normalizar o nome da coluna para o template
                col_name = col.replace(' ', '_')  # Substituir espaços por underscores
                row_data[col_name] = row[col]
       
        data.append(row_data)
   
    # Adiciona status de favorito para cada FII
    if request.user.is_authenticated:
        favorites = UserFavoriteFiis.objects.filter(user=request.user)
        favorite_dict = {fav.fiis.papel: fav.is_favorite for fav in favorites}
    else:
        favorite_dict = {}
   
    # Adiciona o status de favorito em cada linha de dados
    for row in data:
        row['is_favorite'] = favorite_dict.get(row['Papel'], False)
   
    return render(request, 'fiis/index.html', {
        'data': data,
        'columns': columns,
        'filters': filters,
        'setores': segmentos_unicos,
    })


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