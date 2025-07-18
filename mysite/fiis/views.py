from django.shortcuts import render
from django.core.cache import cache
from .fiisdata import rank_fiis

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
    #renomear coluna
    df.rename(columns={'TIPO DE FUNDO': 'TIPO'}, inplace=True)
    segmentos_unicos = df['SEGMENTO'].dropna().unique()
    tipos_unicos = df['TIPO'].dropna().unique()

    # Aplicamos os filtros
    if filters:
        # Dividend Yield
        if 'dividend_yield_min' in filters:
            try:
                min_yield = float(filters['dividend_yield_min'])
                df = df[df['Dividend Yield'] >= min_yield]
            except ValueError:
                pass
        
        # Liquidez
        if 'liquidez_min' in filters:
            try:
                min_liquidez = float(filters['liquidez_min'])
                df = df[df['Liquidez'] >= min_liquidez]
            except ValueError:
                pass
        
        # Vacância
        if 'vacancia_max' in filters:
            try:
                max_vacancia = float(filters['vacancia_max'])
                df = df[df['Vacância Média'] <= max_vacancia]
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
        # if 'segmento' in filters:
        #     segmento = filters['segmento'].strip()
        #     if segmento:
        #         df = df[df['Segmento'].str.contains(segmento, case=False, na=False)]
        if 'SEGMENTO' in filters:
            segmento = filters['SEGMENTO'].strip()
            if segmento:
                df = df[df['SEGMENTO'].str.contains(segmento, case=False, na=False)]
        
        if 'TIPO' in filters:
            tipo = filters['TIPO'].strip()
            if tipo:
                df = df[df['TIPO'].str.contains(tipo, case=False, na=False)]
    
    

    # Recalcular o ranking após os filtros
    df = df.reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)
    df = df.sort_values('Rank')

    # Preparar os dados para o template
    data = df.to_dict('records')
    columns = df.columns.tolist()
    
    return render(request, 'fiis/index.html', {
        'data': data, 
        'columns': columns,
        'filters': filters,
        'SEGMENTO': segmentos_unicos,
        'TIPO': tipos_unicos
    })