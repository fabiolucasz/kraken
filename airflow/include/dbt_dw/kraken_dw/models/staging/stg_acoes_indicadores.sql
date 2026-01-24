with source as (
    select * from {{ ref('acoes_indicadores') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados originais
        p_l,
        p_receita_psr,
        p_vp,
        dy,
        payout,
        margem_líquida as margem_liquida,
        margem_bruta,
        margem_ebit,
        margem_ebitda,
        ev_ebitda,
        ev_ebit,
        p_ebitda,
        p_ebit,
        p_ativo,
        p_capgiro,
        p_ativo_circ_liq,
        vpa,
        lpa,
        giro_ativos,
        roe,
        roic,
        roa,
        dívida_líquida___patrimônio as divida_liquida_patrimonio,
        dívida_líquida___ebitda as divida_liquida_ebitda,
        dívida_líquida___ebit as divida_liquida_ebit,
        dívida_bruta___patrimônio as divida_bruta_patrimonio,
        patrimônio___ativos as patrimonio_ativos,
        passivos___ativos as passivos_ativos,
        liquidez_corrente,
        cagr_receitas_5_anos,
        cagr_lucros_5_anos,

        

        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado