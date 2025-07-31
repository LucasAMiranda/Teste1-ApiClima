# 🌤️ Weather API

Uma API REST Django robusta para dados meteorológicos com cache, rate limiting e testes abrangentes.

## 📋 Índice

- [Características](#-características)
- [Como Rodar Local](#-como-rodar-local)
- [Decisões Técnicas](#-decisões-técnicas-principais)
- [O que Faria com Mais Tempo](#-o-que-faria-com-mais-tempo)
- [API Endpoints](#-api-endpoints)
- [Arquitetura](#-arquitetura)
- [Testes](#-testes)
- [Monitoramento](#-monitoramento)

## ✨ Características

- ✅ **API REST completa** com Django REST Framework
- ✅ **Cache inteligente** com Redis (10 minutos)
- ✅ **Banco PostgreSQL** para histórico de consultas
- ✅ **Rate limiting** (100 requisições/hora por IP)
- ✅ **Testes abrangentes** (unitário + integração + E2E)
- ✅ **Docker Compose** para desenvolvimento
- ✅ **Celery** para tarefas assíncronas
- ✅ **Logging estruturado** com rotação
- ✅ **Documentação Swagger** interativa
- ✅ **Segurança** com containers não-root
- ✅ **CI/CD ready** com GitHub Actions

## 🚀 Como Rodar Local

### Pré-requisitos

\`\`\`bash
# Instalar dependências
- Docker & Docker Compose
- Make (opcional, mas recomendado)
- Git
\`\`\`

### Setup Rápido (5 minutos)

\`\`\`bash
# 1. Clonar repositório
git clone <repo-url>
cd weather-api

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e adicionar sua API key da OpenWeatherMap:
# OPENWEATHER_API_KEY=sua_chave_aqui

# 3. Setup completo com um comando
make setup
\`\`\`

### Setup Manual (Passo a Passo)

\`\`\`bash
# 1. Build dos containers
make build

# 2. Iniciar serviços
make up

# 3. Aguardar serviços (30s)
sleep 30

# 4. Executar migrações
make migrate

# 5. Criar superuser (opcional)
make superuser

\`\`\`bash
# 6 Crie um ambiente virtual, ative o ambiente e Instale as dependências do projeto no arquivo requirements.txt 
python3 -m venv venv ou python -m venv venv no windows
source venv/bin/activate -> Linux
venv\Scripts\activate -> Windows
pip install -r requirements.txt

\`\`\`bash
# 7 RODAR LOCALMENTE
python3 manage.py runserver

\`\`\`bash
# 8 Criar superuser 
python3 manage.py createsuperuser

\`\`\`bash
# 9 Container com docker compose e docker file
sudo docker-compose build -up ou sudo docker compose build

\`\`\`bash
# 10 Executando o projeto com docker

    Construa a imagem: docker build -t nome-da-imagem . (execute no diretório onde o Dockerfile está)
    Inicie os containers: docker-compose up (execute no diretório onde o docker-compose.yml está) 
    Acessando o aplicativo:

    Abra o seu navegador e vá para http://localhost:8000 (ou a porta configurada no docker-compose.yml). 
    
    Comandos úteis:

    docker-compose down: Para parar os containers.
    docker-compose up -d: Para executar os containers em background.
    docker ps: Lista os containers em execução.
    docker exec -it nome_do_container bash: Acessa o terminal de um container. 


### Verificar se Está Funcionando

\`\`\`bash
# Health check
curl http://localhost:8000/api/v1/health/

# Teste da API
curl -X POST http://localhost:8000/api/v1/weather/ \
  -H "Content-Type: application/json" \
  -d '{"city": "São Paulo", "country": "BR"}'

# Ver histórico
curl http://localhost:8000/api/v1/weather/history/
\`\`\`

### Acessar Interfaces

- **API Base**: http://localhost:8000/api/v1/
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Django Admin**: http://localhost:8000/admin/ (admin/admin123)

### Comandos Úteis

\`\`\`bash
# Ver logs em tempo real
make logs

# Executar testes
make test

# Parar serviços
make down

# Limpeza completa
make clean

# Shell Django
make shell
\`\`\`

## 🏗️ Decisões Técnicas Principais

### 1. **Arquitetura em Camadas**

\`\`\`
┌─────────────────┐
│   API Layer     │ ← Django REST Framework
├─────────────────┤
│ Business Logic  │ ← Services (weather/services.py)
├─────────────────┤
│   Data Layer    │ ← Models + Cache
├─────────────────┤
│ Infrastructure  │ ← PostgreSQL + Redis + Celery
└─────────────────┘
\`\`\`

**Por quê?**
- **Separação clara** de responsabilidades
- **Testabilidade** individual de cada camada
- **Manutenibilidade** e evolução independente
- **Reutilização** de lógica de negócio

### 2. **Cache Strategy: Write-Through**

```python
def get_weather(self, city, country):
    # 1. Tentar cache primeiro
    cached = cache.get(cache_key)
    if cached:
        return cached, True
    
    # 2. Buscar na API
    data = self._fetch_from_api(city, country)
    
    # 3. Salvar no banco
    WeatherQuery.objects.create(**data)
    
    # 4. Cachear resultado
    cache.set(cache_key, data, timeout=600)
    
    return data, False
