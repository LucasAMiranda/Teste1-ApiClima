# Setup Rápido - Weather API

## 1. Configuração da API Key

1. Edite o arquivo `.env` e substitua `sua_api_key_aqui` pela sua chave da OpenWeatherMap:
   \`\`\`
   OPENWEATHER_API_KEY=sua_chave_real_aqui
   \`\`\`

## 2. Iniciar o projeto

\`\`\`bash
# Setup completo (uma única vez)
make setup

# Ou passo a passo:
make build
make up
make migrate
\`\`\`

## 3. Testar a API

\`\`\`bash
# Teste básico
curl -X POST http://localhost:8000/api/v1/weather/ \
  -H "Content-Type: application/json" \
  -d '{"city": "São Paulo", "country": "BR"}'

# Ver histórico
curl http://localhost:8000/api/v1/weather/history/

# Health check
curl http://localhost:8000/api/v1/health/
\`\`\`

## 4. Acessar documentação

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 5. Logs

\`\`\`bash
# Ver logs em tempo real
make logs

# Logs específicos
docker-compose logs web
docker-compose logs celery
\`\`\`

## Solução de Problemas

### Erro de conexão com banco:
\`\`\`bash
make down
make up
sleep 10
make migrate
\`\`\`

### Erro de API Key:
- Verifique se a chave está correta no arquivo `.env`
- Reinicie os containers: `make down && make up`

### Erro de permissão:
\`\`\`bash
chmod +x scripts/start.sh
make build
