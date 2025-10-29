-- Criar schemas apenas se não existirem
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================
-- Tabela: fiis_kpi
-- ============================================
CREATE TABLE IF NOT EXISTS bronze.fiis_kpi (
    id SERIAL PRIMARY KEY,
    cotação NUMERIC(15, 2),
    dy NUMERIC(10, 2),
    pvp NUMERIC(10, 2),
    liquidez_diária NUMERIC(50, 2),
    liquidez_unidade VARCHAR(20),
    variação NUMERIC(10, 2),
    papel VARCHAR(20) UNIQUE NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Tabela: fiis_info
-- ============================================
CREATE TABLE IF NOT EXISTS bronze.fiis_info (
    id SERIAL PRIMARY KEY,
    razão_social VARCHAR(200),
    cnpj VARCHAR(50),
    público_alvo VARCHAR(100),
    mandato VARCHAR(100),
    segmento VARCHAR(100),
    tipo_de_fundo VARCHAR(100),
    prazo_de_duração VARCHAR(100),
    tipo_de_gestão VARCHAR(100),
    taxa_de_administração VARCHAR(100),
    vacância NUMERIC(10, 2),
    numero_de_cotistas INTEGER,
    cotas_emitidas BIGINT,
    val_patrimonial_p_cota NUMERIC(10, 2),
    valor_patrimonial NUMERIC(20, 2),
    último_rendimento NUMERIC(15, 2),
    valor_patrimonial_unidade VARCHAR(20),
    papel VARCHAR(20) UNIQUE NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ============================================
-- Tabela: fiis_funds_explorer
-- ============================================
CREATE TABLE IF NOT EXISTS bronze.fiis_funds_explorer (
    id SERIAL PRIMARY KEY,
    papel VARCHAR(20) UNIQUE NOT NULL,
    setor VARCHAR(100),
    cotacao NUMERIC(15, 2),
    liquidez_diaria_rs NUMERIC(20, 2),
    ultimo_dividendo NUMERIC(15, 2),
    dividend_yield NUMERIC(15, 2),
    dy_3m_acumulado NUMERIC(15, 2),
    dy_6m_acumulado NUMERIC(15, 2),
    dy_12m_acumulado NUMERIC(15, 2),
    dy_3m_media NUMERIC(15, 2),
    dy_6m_media NUMERIC(15, 2),
    dy_12m_media NUMERIC(15, 2),
    dy_ano NUMERIC(15, 2),
    variacao_preco NUMERIC(15, 2),
    rentab_periodo NUMERIC(15, 2),
    rentab_acumulada NUMERIC(15, 2),
    patrimonio_liquido NUMERIC(20, 2),
    vpa NUMERIC(20, 2),
    p_vpa NUMERIC(20, 2),
    dy_patrimonial NUMERIC(15, 2),
    variacao_patrimonial NUMERIC(15, 2),
    rentab_patr_periodo NUMERIC(15, 2),
    rentab_patr_acumulada NUMERIC(15, 2),
    quant_ativos INTEGER,
    volatilidade NUMERIC(15, 2),
    num_cotistas INTEGER,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ============================================
-- Tabela: acoes
-- ============================================
CREATE TABLE IF NOT EXISTS bronze.acoes_kpi (
    id SERIAL PRIMARY KEY,
    cotação NUMERIC(15, 2),
    variação_12m NUMERIC(15, 2),
    p_l NUMERIC(15, 2),
    p_vp NUMERIC(15, 2),
    dy NUMERIC(15, 2),
    carteira_investidor_10 VARCHAR(50),
    papel VARCHAR(20) UNIQUE NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze.acoes_img (
    id SERIAL PRIMARY KEY,
    papel VARCHAR(10) UNIQUE NOT NULL,
    ticker_img VARCHAR(2000),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze.acoes_info (
    id SERIAL PRIMARY KEY,
    valor_de_mercado NUMERIC(20, 2),
    valor_de_firma NUMERIC(20, 2),
    patrimônio_líquido NUMERIC(20, 2),
    n_total_de_papeis NUMERIC(20, 2),
    ativos NUMERIC(20, 2),
    ativo_circulante NUMERIC(20, 2),
    dívida_bruta NUMERIC(20, 2),
    dívida_líquida NUMERIC(20, 2),
    disponibilidade NUMERIC(20, 2),
    --tag_along NUMERIC(15, 2),
    tag_along VARCHAR(20),
    segmento_de_listagem VARCHAR(255),
    free_float NUMERIC(15, 2),
    setor VARCHAR(255),
    segmento VARCHAR(255),
    papel VARCHAR(20) UNIQUE NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze.acoes_indicadores (
    id SERIAL PRIMARY KEY,
    p_l NUMERIC(15, 2),
    p_receita_psr NUMERIC(15, 2),
    p_vp NUMERIC(15, 2),
    dy NUMERIC(15, 2),
    payout NUMERIC(15, 2),
    margem_líquida NUMERIC(15, 2),
    margem_bruta NUMERIC(15, 2),
    margem_ebit NUMERIC(15, 2),
    margem_ebitda NUMERIC(15, 2),
    ev_ebitda NUMERIC(15, 2),
    ev_ebit NUMERIC(15, 2),
    p_ebitda NUMERIC(15, 2),
    p_ebit NUMERIC(15, 2),
    p_ativo NUMERIC(15, 2),
    p_capgiro NUMERIC(15, 2),
    p_ativo_circ_liq NUMERIC(15, 2),
    vpa NUMERIC(15, 2),
    lpa NUMERIC(15, 2),
    giro_ativos NUMERIC(15, 2),
    roe NUMERIC(15, 2),
    roic NUMERIC(15, 2),
    roa NUMERIC(15, 2),
    dívida_líquida___patrimônio NUMERIC(15, 2),
    dívida_líquida___ebitda NUMERIC(15, 2),
    dívida_líquida___ebit NUMERIC(15, 2),
    dívida_bruta___patrimônio NUMERIC(15, 2),
    patrimônio___ativos NUMERIC(15, 2),
    passivos___ativos NUMERIC(15, 2),
    liquidez_corrente NUMERIC(15, 2),
    cagr_receitas_5_anos NUMERIC(15, 2),
    cagr_lucros_5_anos NUMERIC(15, 2),
    papel VARCHAR(20) UNIQUE NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);