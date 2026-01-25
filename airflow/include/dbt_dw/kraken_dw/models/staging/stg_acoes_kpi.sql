with source as (
    select * from {{ ref('acoes_kpi') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados KPI originais
        cotação as cotacao,
        variação_12m,
        p_l,
        p_vp,
        dy,
        

        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado