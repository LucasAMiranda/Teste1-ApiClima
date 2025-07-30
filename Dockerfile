# Base oficial do Python
FROM python:3.10-slim

# Evita criação de arquivos .pyc e ativa flush do stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define diretório de trabalho no container
WORKDIR /app

# Instala dependências do sistema para psycopg2 e Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    musl-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requirements primeiro para cache de build eficiente
COPY requirements.txt /app/

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o projeto
COPY . /app/

# Expõe a porta do Django
EXPOSE 8000

# Comando padrão (vai ser sobrescrito no docker-compose.yml se quiser)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
