with source as (
    select * from {{ ref('fiis_fundsexplorer') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados KPI
        setor,
        preço_atual,
        liquidez_diária as liquidez_diaria,
        p_vp,
        último_dividendo as ultimo_dividendo,
        dividend_yield,
        dy_3m_acumulado,
        dy_6m_acumulado,
        dy_12m_acumulado,
        dy_3m_média as dy_3m_media,
        dy_6m_média as dy_6m_media,
        dy_12m_média as dy_12m_media,
        dy_ano,
        variação_preço as variacao_preco,
        rentab_período as rentab_periodo,
        rentab_acumulada,
        patrimônio_líquido as patrimonio_liquido,
        vpa,
        p_vpa,
        dy_patrimonial,
        variação_patrimonial as variacao_patrimonial,
        rentab_patr_período as rentab_patr_periodo,
        rentab_patr_acumulada,
        quant_ativos,
        volatilidade,
        num_cotistas,
        tax_gestão as tax_gestao,
        tax_performance,
        tax_administração as tax_administracao,

        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado