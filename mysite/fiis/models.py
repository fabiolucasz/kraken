from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class Fiis(models.Model):
    # Identificação
    papel = models.CharField(max_length=10, unique=True)
    setor = models.CharField(max_length=100, blank=True, null=True)
    
    # Preços e Valores
    preco_atual = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    liquidez_diaria = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    p_vp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ultimo_dividendo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    # Dividend Yields
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_3m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_6m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_12m_acumulado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_3m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_6m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_12m_media = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_ano = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Variações e Rentabilidades
    variacao_preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rentabilidade_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rentabilidade_acumulada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Patrimônio e VPA
    patrimonio_liquido = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    vpa = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    p_vpa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dy_patrimonial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    variacao_patrimonial = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rentabilidade_patr_periodo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rentabilidade_patr_acumulada = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Outras Informações
    quant_ativos = models.IntegerField(blank=True, null=True)
    volatilidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    num_cotistas = models.IntegerField(blank=True, null=True)
    taxa_gestao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    taxa_performance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    taxa_administracao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Datas
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fundo Imobiliário'
        verbose_name_plural = 'Fundos Imobiliários'
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
        unique_together = ('user', 'fiis')
        verbose_name = 'Favorito do Usuário'
        verbose_name_plural = 'Favoritos dos Usuários'

    def __str__(self):
        return f"{self.user.username} - {self.fiis.papel}"
