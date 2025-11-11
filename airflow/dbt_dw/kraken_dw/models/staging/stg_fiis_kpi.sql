with source as (
    select * from {{ ref('fiis_kpis') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados KPI
        cotação as cotacao,
        dy as dividend_yield,
        pvp,
        liquidez_diária as liquidez_diaria,
        liquidez_unidade,
        variação as variacao,
        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado