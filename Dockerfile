# Use Python 3.11 como base
FROM python:3.11-slim

# Configurar proxy para build (argumentos passados do docker-compose)
ARG HTTP_PROXY=http://proxy.prodemge.gov.br:8080
ARG HTTPS_PROXY=http://proxy.prodemge.gov.br:8080
ARG NO_PROXY=localhost,127.0.0.1

# Definir proxy como variáveis de ambiente durante o build
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}
ENV no_proxy=${NO_PROXY}

# Instalar dependências do sistema para Chrome e Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && wget -q -O /tmp/google-signing-key.pub https://dl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-signing-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/google-signing-key.pub

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Expor a porta do FastAPI
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
