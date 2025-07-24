from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import Acoes, UserFavoriteAcoes
from django.contrib import messages
from django.shortcuts import redirect
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def index(request):

    df = pd.read_csv('./../acoes.csv', quotechar='"', sep=',', decimal='.', encoding='utf-8', skipinitialspace=True)

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