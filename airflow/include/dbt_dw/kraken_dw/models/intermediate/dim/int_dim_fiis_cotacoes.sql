{{
    config(
        materialized = 'table',
        unique_key = 'sk_papel',
        tags = ['intermediate', 'dimension']
    )
}}

with fiis as (
    select * from {{ ref('stg_fiis_kpi') }}
)

select
    -- Chave substituta (surrogate key)
    {{ dbt_utils.generate_surrogate_key(['papel']) }} as sk_papel,
    
    -- Chave de negócio
    papel,
    
    -- Atributos descritivos
    valor_cota,
    
    
    -- Datas importantes
    data_cotacao,
    
    -- Metadados
    current_timestamp as dbt_updated_at,
    '{{ run_started_at }}' as dbt_loaded_at
from fiis