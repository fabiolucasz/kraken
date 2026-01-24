with source as (
    select * from {{ ref('acoes_info') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados KPI
        valor_de_mercado,
        valor_de_firma,
        patrimônio_líquido as patrimonio_liquido,
        n_total_de_papeis,
        ativos,
        ativo_circulante,
        dívida_bruta as divida_bruta,
        dívida_líquida as divida_liquida,
        disponibilidade,
        segmento_de_listagem,
        free_float,
        tag_along,
        liquidez_média_diária as liquidez_media_diaria,
        setor,
        segmento,

        
        
        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado