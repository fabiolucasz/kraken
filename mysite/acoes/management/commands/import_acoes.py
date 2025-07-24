from django.core.management.base import BaseCommand
from acoes.acoedata import import_acoes_from_csv

class Command(BaseCommand):
    help = 'Importa as Ações do arquivo df1.csv para o banco de dados'

    def handle(self, *args, **options):
        success = import_acoes_from_csv()
        if success:
            self.stdout.write(self.style.SUCCESS('Ações importadas com sucesso!'))
        else:
            self.stdout.write(self.style.ERROR('Erro ao importar Ações'))
