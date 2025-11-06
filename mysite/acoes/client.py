import requests
from django.conf import settings

class KrakenAPIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or getattr(settings, 'KRAKEN_API_URL', 'http://localhost:8000')

    def get_acoes_ranking(self):
        """Busca o ranking de ações da API"""
        response = requests.get(f"{self.base_url}/acoes_ranking")
        response.raise_for_status()
        return response.json() 