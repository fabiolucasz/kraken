# 🏦 Kraken - Análise de Investimentos

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Pandas-2.3-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Scikit--learn-1.7.0-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</div>

## 📋 Visão Geral

O Kraken é uma plataforma web para análise e rankeamento de ativos financeiros (FIIs e Ações) com base em indicadores fundamentais. A ferramenta utiliza técnicas de machine learning para classificar os melhores investimentos de acordo com critérios personalizáveis.

## ✨ Funcionalidades

- 🏦 Análise detalhada de FIIs e Ações
- 📊 Rankeamento inteligente baseado em múltiplos indicadores
- 🔍 Filtros avançados para busca de ativos
- ⭐ Sistema de favoritos para acompanhamento
- 📈 Visualização clara dos principais indicadores financeiros
- 🚀 Interface responsiva e moderna

## 🛠️ Tecnologias

- **Backend:** Django 5.2
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Análise de Dados:** Pandas, Scikit-learn
- **Web Scraping:** Scrapy, BeautifulSoup, Selenium
- **Containerização:** Docker, Docker Compose
- **Outras:** aiohttp, lxml, html5lib

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Git
- Docker e Docker Compose (opcional para instalação com Docker)

### Método 1: Instalação Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/fabiolucasz/kraken.git
   cd kraken
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv .venv # Cria um ambiente virtual windows
   python3 -m venv .venv # Cria um ambiente virtual linux

   source .venv/bin/activate  # Ativar o ambiente virtual (Linux/Mac)
   # ou
   .venv\Scripts\activate  # Ativar o ambiente virtual (Windows)
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   SECRET_KEY=sua_chave_secreta_aqui
   DEBUG=True
   ```

5. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

8. **Acesse o sistema**
   Abra seu navegador em: http://127.0.0.1:8000/

### Método 2: Usando Docker

1. **Clone o repositório**
   ```bash
   git clone https://github.com/fabiolucasz/kraken.git
   cd kraken
   ```

2. **Crie o arquivo .env**
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` conforme necessário.

3. **Construa e inicie os contêineres**
   ```bash
   docker-compose up --build -d
   ```

4. **Execute as migrações**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Crie um superusuário (opcional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Acesse o sistema**
   Abra seu navegador em: http://localhost:8000/

## 📊 Estrutura do Projeto

```
kraken/
├── mysite/                  # Projeto Django principal
│   ├── acoes/              # App de ações
│   ├── fiis/               # App de FIIs
│   ├── mysite/             # Configurações do projeto
│   ├── manage.py
│   └── requirements.txt
├── scraper/                # Spiders para coleta de dados
├── static/                 # Arquivos estáticos
├── media/                  # Arquivos de mídia
├── docker-compose.yml
└── Dockerfile
```

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Adicione suas mudanças (`git add .`)
4. Comite suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Faça o Push da Branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## ✉️ Contato

Fabio Lucas - [LinkedIn](https://www.linkedin.com/in/fabiolucamz/)

Link do Projeto: [https://github.com/fabiolucasz/kraken](https://github.com/fabiolucasz/kraken)

## 📌 Agradecimentos

- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Pandas](https://pandas.pydata.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [Todos os contribuidores](../../contributors)