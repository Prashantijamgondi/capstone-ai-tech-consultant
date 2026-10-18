FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings httpx beautifulsoup8 lxml python-dotenv pytest

RUN cd task2-inbox-agent && npm install && npm run build

EXPOSE 8080

CMD ["python", "server.py"]
