# Nome da imagem
IMAGE_NAME=meu_django_app
CONTAINER_NAME=django_app
PORT=8000

# Variáveis de banco (pode vir do .env)
DB_HOST=db
DB_PORT=5432

# =======================
# Comandos principais
# =======================

# Build da imagem Docker
build:
	docker build -t $(IMAGE_NAME) .

# Rodar container interativo (sem Postgres externo)
run:
	docker run -it --rm --name $(CONTAINER_NAME) \
		-p $(PORT):8000 \
		-e DB_HOST=$(DB_HOST) \
		-e DB_PORT=$(DB_PORT) \
		$(IMAGE_NAME)

# Rodar container em segundo plano
start:
	docker run -d --name $(CONTAINER_NAME) \
		-p $(PORT):8000 \
		-e DB_HOST=$(DB_HOST) \
		-e DB_PORT=$(DB_PORT) \
		$(IMAGE_NAME)

# Parar container
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Executar migrações no container rodando
migrate:
	docker exec -it $(CONTAINER_NAME) python3 manage.py migrate

# Criar superusuário Django
createsuperuser:
	docker exec -it $(CONTAINER_NAME) python3 manage.py createsuperuser

# Ver logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Limpar containers e imagens
clean:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true
	docker system prune -f

# =======================
# Testes
# =======================

# Rodar pytest dentro do container
test:
	docker exec -it $(CONTAINER_NAME) pytest --disable-warnings -v --cov=weather --cov-report=term-missing
