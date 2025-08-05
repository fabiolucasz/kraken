from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Acoes(models.Model):
    papel = models.CharField(max_length=10, unique=True)
    cotation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    variation_12m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pv = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    psr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_liquida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_bruta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_ebit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    margem_ebitda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ev_ebitda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ev_ebit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pebitda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pebit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pativo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    p_cap_giro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    p_ativo_circ_liq = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vpa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lpa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    giro_ativos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roic = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    divida_liquida_patrimonio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    divida_liquida_ebitda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    divida_liquida_ebit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    divida_bruta_patrimonio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    patrimonio_ativos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    passivos_ativos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    liquidez_corrente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cagr_receitas_5_anos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cagr_lucros_5_anos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_mercado = models.BigIntegerField(null=True, blank=True)
    valor_firma = models.BigIntegerField(null=True, blank=True)
    patrimonio_liquido = models.BigIntegerField(null=True, blank=True)
    numero_papeis = models.BigIntegerField(null=True, blank=True)
    ativos = models.BigIntegerField(null=True, blank=True)
    ativo_circulante = models.BigIntegerField(null=True, blank=True)
    divida_bruta = models.BigIntegerField(null=True, blank=True)
    divida_liquida = models.BigIntegerField(null=True, blank=True)
    disponibilidade = models.BigIntegerField(null=True, blank=True)
    segmento_listagem = models.CharField(max_length=255, null=True, blank=True)
    free_float = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tag_along = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    setor = models.CharField(max_length=255, null=True, blank=True)
    segmento = models.CharField(max_length=255, null=True, blank=True)
    ticker_img = models.URLField(max_length=2000, null=True, blank=True)

    class Meta:
        ordering = ['papel']

class UserFavoriteAcoes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acoes = models.ForeignKey(Acoes, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'acoes')
        verbose_name = 'Favorito do Usuário'
        verbose_name_plural = 'Favoritos dos Usuários'

    def __str__(self):
        return f"{self.user.username} - {self.acoes.papel}"
