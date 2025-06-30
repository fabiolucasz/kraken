from django.db import models

# Create your models here.
class Fiis(models.Model):
    #df1
    favoritos = models.BooleanField(default=False)
    papel = models.CharField(max_length=10, unique=True)
    segmento = models.CharField(max_length=50)
    cotacao = models.FloatField()
    ffo_yield = models.FloatField()
    dividend_yield = models.FloatField()
    pvp = models.FloatField()
    valor_mercado = models.IntegerField()
    liquidez = models.IntegerField()
    qtd_imoveis = models.IntegerField()
    cap_rate = models.FloatField()
    vacancia_media = models.FloatField()

    #df2
    razao_social = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    publico_alvo = models.CharField(max_length=50)
    mandato = models.CharField(max_length=50)
    segmento = models.CharField(max_length=50)
    tipo_fundo = models.CharField(max_length=50)
    prazo_duracao = models.CharField(max_length=50)
    tipo_gestao = models.CharField(max_length=50)
    taxa_administracao = models.CharField(max_length=50)
    vacancia = models.FloatField()
    numero_cotistas = models.IntegerField()
    cotas_emitidas = models.IntegerField()
    valor_patrimonial_cota = models.FloatField()
    valor_patrimonial = models.CharField(max_length=50)
    ultimo_rendimento = models.FloatField()
    dividend_yield_12_meses = models.FloatField()

    #Cálculos
    yield_on_coast = models.FloatField()


    pub_date_time = models.DateTimeField(auto_now_add=True)

