from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Acoes(models.Model):
    papel = models.CharField(max_length=10, unique=True)

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
