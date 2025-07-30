FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Atualizar e instalar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    libpq-dev \
    postgresql-client \
    netcat \
    curl \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Criar usuário não-root
RUN groupadd -r -g 1000 django && \
    useradd -r -u 1000 -g django -d /app -s /bin/bash django

# Copiar requirements e instalar Python packages
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copiar o projeto e ajustar permissões
COPY --chown=django:django . .

RUN mkdir -p /app/logs /app/staticfiles /app/media \
    && chown -R django:django /app \
    && chmod -R 755 /app \
    && chmod +x scripts/*.sh

# Limpar arquivos Python bytecode
RUN find /app -name "*.pyc" -delete && find /app -name "__pycache__" -type d -exec rm -rf {} +

USER django

# Coletar arquivos estáticos
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["./scripts/start.sh"]
