-- ============================================
-- Tabela: acoes_ranking
-- ============================================
CREATE TABLE gold.acoes_ranking AS
SELECT 
    ai.*,
    ai_kpi.cotação as cotacao_atual,
    ai_kpi.variação_12m,
    ai_kpi.p_l,
    ai_kpi.p_vp,
    ai_kpi.dy,
    aimg.ticker_img,
    aind.p_receita_psr,
    aind.payout,
    aind.margem_líquida,
    aind.margem_bruta,
    aind.margem_ebit,
    aind.margem_ebitda,
    aind.ev_ebitda,
    aind.ev_ebit,
    aind.p_ebitda,
    aind.p_ebit,
    aind.p_ativo,
    aind.p_capgiro,
    aind.p_ativo_circ_liq,
    aind.vpa,
    aind.lpa,
    aind.giro_ativos,
    aind.roe,
    aind.roic,
    aind.roa,
    aind."dívida_líquida___patrimônio" as divida_liquida_patrimonio,
    CURRENT_TIMESTAMP as data_processamento
FROM 
    silver.acoes_info ai
LEFT JOIN 
    bronze.acoes_kpi ai_kpi ON ai.papel = ai_kpi.papel
LEFT JOIN 
    bronze.acoes_img aimg ON ai.papel = aimg.papel
LEFT JOIN 
    bronze.acoes_indicadores aind ON ai.papel = aind.papel;

ALTER TABLE gold.acoes_ranking ADD PRIMARY KEY (id);

-- ============================================
-- Tabela: fiis_ranking
-- ============================================
CREATE TABLE gold.fiis_ranking AS
SELECT 
    fi.*,
    fk.cotação as cotacao_atual,
    fk.dy as dividend_yield,
    fk.pvp,
    fk.liquidez_diária,
    fk.liquidez_unidade,
    fk.variação as variacao_diaria,
    CURRENT_TIMESTAMP as data_processamento
FROM 
    silver.fiis_info fi
LEFT JOIN 
    bronze.fiis_kpi fk ON fi.papel = fk.papel;

ALTER TABLE gold.fiis_ranking ADD PRIMARY KEY (id);
