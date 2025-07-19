from django.core.management.base import BaseCommand
from fiis.fiisdata import import_fiis_from_csv

class Command(BaseCommand):
    help = 'Importa os FIIs do arquivo df1.csv para o banco de dados'

    def handle(self, *args, **options):
        success = import_fiis_from_csv()
        if success:
            self.stdout.write(self.style.SUCCESS('FIIs importados com sucesso!'))
        else:
            self.stdout.write(self.style.ERROR('Erro ao importar FIIs'))
