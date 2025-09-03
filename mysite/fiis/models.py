from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Fiis(models.Model):

    papel = models.CharField(max_length=20, unique=True, verbose_name='Papel')
    setor = models.CharField(max_length=100, blank=True, null=True, verbose_name='Setor')
    preco_atual = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Preço Atual (R$)')
    liquidez_diaria_rs = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Liquidez Diária (R$)')
    ultimo_dividendo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Último Dividendo')
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Dividend Yield')
    dy_3m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (3M) Acumulado')
    dy_6m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (6M) Acumulado')
    dy_12m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (12M) Acumulado')
    dy_3m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (3M) média')
    dy_6m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (6M) média')
    dy_12m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (12M) média')
    dy_ano = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY Ano')
    variacao_preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação Preço')
    rentab_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Rentab. Período')
    rentab_acumulada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Rentab. Acumulada')
    patrimonio_liquido = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Patrimônio Líquido')
    vpa = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='VPA')
    p_vpa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='P/VPA')
    dy_patrimonial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY Patrimonial')
    variacao_patrimonial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação Patrimonial')
    rentab_patr_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Rentab. Patr. Período')
    rentab_patr_acumulada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Rentab. Patr. Acumulada')
    quant_ativos = models.IntegerField(blank=True, null=True, verbose_name='Quant. Ativos')
    volatilidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Volatilidade')
    num_cotistas = models.IntegerField(blank=True, null=True, verbose_name='Nº de Cotistas')
    cotacao = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Cotação')
    dy = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY')
    pvp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='P/VP')
    liquidez_diaria = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Liquidez Diária')
    liquidez_unidade = models.CharField(max_length=20, blank=True, null=True, verbose_name='Liquidez por Unidade')
    variacao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação')
    razao_social = models.CharField(max_length=200, blank=True, null=True, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name='CNPJ')
    publico_alvo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Público-Alvo')
    mandato = models.CharField(max_length=100, blank=True, null=True, verbose_name='Mandato')
    segmento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Segmento')
    tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de Fundo')
    prazo_duracao = models.CharField(max_length=100, blank=True, null=True, verbose_name='Prazo de Duração')
    tipo_gestao = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de Gestão')
    vacancia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Vacância')
    cotas_emitidas = models.BigIntegerField(blank=True, null=True, verbose_name='Cotas Emitidas')
    valor_patrimonial_cota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação Patrimonial')
    valor_patrimonial = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Valor Patrimonial')
    ultimo_rendimento = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Último Rendimento')
    valor_patrimonial_unidade = models.CharField(max_length=20, blank=True, null=True, verbose_name='Valor Patrimonial por Unidade')
 
    # Datas
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "fiis"
        verbose_name = 'Fundo Imobiliário'
        verbose_name_plural = 'Fundos Imobiliários'
        ordering = ['papel']
    
    def __str__(self):
        return self.papel

class FiisKpi(models.Model):
    __tablename__ = "fiis_kpi"
    papel = models.CharField(max_length=20, unique=True, verbose_name='Papel')
    cotacao = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Cotação')
    dy_12m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='DY (12M)')
    pvp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='PVP')
    liquidez_diaria = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Liquidez Diária')
    liquidez_diaria_unidade = models.CharField(max_length=20, blank=True, null=True, verbose_name='Liquidez por Unidade')
    variacao_12m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação 12M')

    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fiis_kpi"
        verbose_name = 'KPI do FII'
        verbose_name_plural = 'KPIs dos FII'
        ordering = ['papel']
    
    def __str__(self):
        return self.papel
    
class FiisInfo(models.Model):
    __tablename__ = "fiis_info"
    papel = models.CharField(max_length=20, unique=True, verbose_name='Papel')
    razao_social = models.CharField(max_length=200, blank=True, null=True, verbose_name='Razão Social')
    cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name='CNPJ')
    publico_alvo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Público-Alvo')
    mandato = models.CharField(max_length=100, blank=True, null=True, verbose_name='Mandato')
    segmento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Segmento')
    tipo_fundo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de Fundo')
    prazo_duracao = models.CharField(max_length=100, blank=True, null=True, verbose_name='Prazo de Duração')
    tipo_gestao = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de Gestão')
    taxa_administracao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Taxa de Administração')
    vacancia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Vacância')
    numero_cotistas = models.IntegerField(blank=True, null=True, verbose_name='Nº de Cotistas')
    cotas_emitidas = models.BigIntegerField(blank=True, null=True, verbose_name='Cotas Emitidas')
    valor_patrimonial_cota = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Variação Patrimonial')
    valor_patrimonial = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name='Valor Patrimonial')
    ultimo_rendimento = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Último Rendimento')
    valor_patrimonial_unidade = models.CharField(max_length=20, blank=True, null=True, verbose_name='Valor Patrimonial por Unidade')
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "fiis_info"
        verbose_name = 'Informações do FII'
        verbose_name_plural = 'Informações dos FII'
        ordering = ['papel']
    
    def __str__(self):
        return self.papel
    

class UserFavoriteFiis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fiis = models.ForeignKey(Fiis, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_favorite_fiis"
        unique_together = ('user', 'fiis')
        verbose_name = 'Favorito do Usuário'
        verbose_name_plural = 'Favoritos dos Usuários'

    def __str__(self):
        return f"{self.user.username} - {self.fiis.papel}"
