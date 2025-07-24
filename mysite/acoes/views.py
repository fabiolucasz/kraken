from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import Acoes, UserFavoriteAcoes
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def rank_acoes():
    df = pd.read_csv('./../acoes.csv', quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)
    
    indicadores = {
        'DY': 1,
        'P/L': 1,
        'PAYOUT': 1,
        'P/VP': -1,
        'ROE': 1,
    }
    
    scaler = MinMaxScaler()


    for col, peso in indicadores.items():
        # Normalizar entre 0 e 1
        norm = scaler.fit_transform(df[[col]])
        if peso < 0:
            norm = 1 - norm  # inverter se menor é melhor
        df[f'{col}_score'] = norm * abs(peso)
    
    df['Rank_ponderado'] = df[[f'{col}_score' for col in indicadores]].sum(axis=1)
    df = df.sort_values(by='Rank_ponderado', ascending=False)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    ordered_df = df[['Rank', 'Papel','Cotação', 'P/L','DY','P/VP','ROE','PAYOUT']]
    df = ordered_df
    
    
    return df

def index(request):

    df = rank_acoes()

    df = df.reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)
    df = df.sort_values('Rank')

    data = []
    columns = df.columns.tolist()
   
    # Adicionar status de favorito para cada Ação se o usuário estiver logado
    if request.user.is_authenticated:
        favorites = UserFavoriteAcoes.objects.filter(user=request.user)
        favorite_dict = {fav.acoes.papel: fav.is_favorite for fav in favorites}
   
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
    
    return render(request, 'acoes/index.html', {'data': data, 'columns': columns})


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