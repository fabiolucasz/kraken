from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Fiis(models.Model):
    papel = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['papel']

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
