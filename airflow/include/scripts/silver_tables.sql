-- ============================================
-- Tabela: fiis
-- ============================================
CREATE TABLE silver.fiis_info AS
SELECT 
    id,
    razão_social,
    cnpj,
    público_alvo,
    mandato,
    segmento,
    tipo_de_fundo,
    prazo_de_duração,
    tipo_de_gestão,
    vacância,
    numero_de_cotistas,
    cotas_emitidas,
    val_patrimonial_p_cota,
    valor_patrimonial,
    último_rendimento,
    valor_patrimonial_unidade,
    papel,
    data_atualizacao
FROM bronze.fiis_info;

ALTER TABLE silver.fiis_info ADD PRIMARY KEY (id);

CREATE UNIQUE INDEX ON silver.fiis_info (papel);

-- ============================================
-- Tabela: acoes
-- ============================================
CREATE TABLE silver.acoes_info AS
SELECT 
    id,
    valor_de_mercado,
    valor_de_firma,
    patrimônio_líquido,
    n_total_de_papeis,
    ativos,
    ativo_circulante,
    dívida_bruta,
    dívida_líquida,
    disponibilidade,
    segmento_de_listagem,
    free_float,
    setor,
    segmento,
    papel,
    data_atualizacao
FROM bronze.acoes_info;

ALTER TABLE silver.acoes_info ADD PRIMARY KEY (id);

CREATE UNIQUE INDEX ON silver.acoes_info (papel);