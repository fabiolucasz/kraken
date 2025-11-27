# Primeiro estágio: Base do Airflow
FROM astrocrpublic.azurecr.io/runtime:3.1-2

RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-postgres==1.9.0 && deactivate

USER root

RUN pip install playwright pandas beautifulsoup4

# Instala o Playwright no diretório padrão
RUN playwright install --with-deps chromium

# Cria o diretório de destino e copia os arquivos do Playwright
RUN mkdir -p /home/astro/.cache/ms-playwright && \
    if [ -d "/root/.cache/ms-playwright" ]; then \
        cp -r /root/.cache/ms-playwright/* /home/astro/.cache/ms-playwright/; \
    fi && \
    chown -R astro:astro /home/astro/.cache

USER astro

