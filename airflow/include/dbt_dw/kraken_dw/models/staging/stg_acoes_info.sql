with source as (
    select * from {{ ref('acoes_info') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados KPI originais
        coalesce(nullif(valor_de_mercado, 'null'), '0') as valor_de_mercado_F,
        case
            when valor_de_mercado ~ '^-?[0-9,\.]+$' 
            then replace(replace(valor_de_mercado, '.', ''), ',', '.')::numeric
            else 0
        end as valor_de_mercado,

        coalesce(nullif(valor_de_firma, 'null'), '0') as valor_de_firma_F,
        case
            when valor_de_firma ~ '^-?[0-9,\.]+$'
            then replace(replace(valor_de_firma, '.', ''), ',', '.')::numeric
            else 0
        end as valor_de_firma,

        coalesce(nullif(patrimônio_líquido, 'null'), '0') as patrimonio_liquido_F,
        case
            when patrimônio_líquido ~ '^-?[0-9,\.]+$'
            then replace(replace(patrimônio_líquido, '.', ''), ',', '.')::numeric
            else 0
        end as patrimonio_liquido,

        coalesce(nullif(n_total_de_papeis, 'null'), '0') as n_total_de_papeis,
        
        coalesce(nullif(ativos, 'null'), '0') as ativos_F,
        case
            when ativos ~ '^-?[0-9,\.]+$'
            then replace(replace(ativos, '.', ''), ',', '.')::numeric
            else 0
        end as ativos,

        coalesce(nullif(ativo_circulante, 'null'), '0') as ativo_circulante_F,
        case
            when ativo_circulante ~ '^-?[0-9,\.]+$'
            then replace(replace(ativo_circulante, '.', ''), ',', '.')::numeric
            else 0
        end as ativo_circulante,
        
        coalesce(nullif(dívida_bruta, 'null'), '0') as divida_bruta_F,
        case
            when dívida_bruta ~ '^-?[0-9,\.]+$'
            then replace(replace(dívida_bruta, '.', ''), ',', '.')::numeric
            else 0
        end as divida_bruta,


        coalesce(nullif(dívida_líquida, 'null'), '0') as divida_liquida_F,
        case
            when dívida_líquida ~ '^-?[0-9,\.]+$'
            then replace(replace(dívida_líquida, '.', ''), ',', '.')::numeric
            else 0
        end as divida_liquida,
        coalesce(nullif(disponibilidade, 'null'), '0') as disponibilidade_F,
        case
            when disponibilidade ~ '^-?[0-9,\.]+$'
            then replace(replace(disponibilidade, '.', ''), ',', '.')::numeric
            else 0
        end as disponibilidade,
        segmento_de_listagem,
        free_float,
        tag_along,
        coalesce(nullif(liquidez_média_diária, 'null'), '0') as liquidez_media_diaria_F,
        case
            when liquidez_média_diária ~ '^-?[0-9,\.]+$'
            then replace(replace(liquidez_média_diária, '.', ''), ',', '.')::numeric
            else 0
        end as liquidez_media_diaria,
        setor,
        segmento,
        

        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado