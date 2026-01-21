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
        
        -- Cálculo da liquidez diária formatada
        case 
            when liquidez_unidade = 'K' then liquidez_diária * 1000
            when liquidez_unidade = 'M' then liquidez_diária * 1000000
            else liquidez_diária  -- Caso não haja unidade definida
        end as liquidez_diaria_F,
        
        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado