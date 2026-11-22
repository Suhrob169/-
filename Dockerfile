FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Мы запускаем ваш сервер (server.py) через gunicorn
# Порт 8000 — это стандарт для Fly.io
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "server:app"]
