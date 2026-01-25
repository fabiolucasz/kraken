with source as (
    select * from {{ ref('fiis_info') }}
),

transformado as (
    select
        -- Chaves
        papel,
        
        -- Dados 
        razão_social as razao_social,
        cnpj,
        público_alvo as publico_alvo,
        mandato,
        segmento,
        tipo_de_fundo as tipo_de_fundo,
        prazo_de_duração as prazo_de_duracao,
        tipo_de_gestão as tipo_de_gestao,
        taxa_de_administração as taxa_de_administracao,
        vacância as vacancia,
        numero_de_cotistas as numero_de_cotistas,
        cotas_emitidas,
        val_patrimonial_p_cota,
        último_rendimento as ultimo_rendimento,
        valor_patrimonial,
        valor_patrimonial_unidade,

        
        -- Cálculo da liquidez diária formatada
        case 
            when valor_patrimonial_unidade = 'Mil' then valor_patrimonial * 1000
            when valor_patrimonial_unidade = 'Milhões' then valor_patrimonial * 1000000
            when valor_patrimonial_unidade = 'Bilhão' then valor_patrimonial * 1000000000
            when valor_patrimonial_unidade = 'Bilhões' then valor_patrimonial * 1000000000
            else valor_patrimonial  -- Caso não haja unidade definida
        end as valor_patrimonial_F,
        
        -- Metadados
        current_timestamp as etl_inserted_at
        
    from source
)

select * from transformado