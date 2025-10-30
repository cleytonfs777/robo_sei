# Criador de Ofícios SEI - Docker

## 📋 Pré-requisitos

- **Docker Desktop** instalado e rodando
  - Windows: https://www.docker.com/products/docker-desktop
  - Certifique-se de que o Docker Desktop está rodando antes de executar

## 🚀 Como usar

### Opção 1: Script Automático (Recomendado)

Basta executar o arquivo `start-docker.bat`:

```bash
start-docker.bat
```

O script irá:
1. ✅ Verificar se o Docker está instalado
2. ✅ Verificar se o arquivo `.env` existe
3. ✅ Construir a imagem Docker
4. ✅ Iniciar o container
5. ✅ Abrir o navegador automaticamente

### Opção 2: Comandos Manuais

#### Construir e iniciar pela primeira vez:
```bash
docker-compose up --build -d
```

#### Iniciar (após já ter construído):
```bash
docker-compose up -d
```

#### Parar o container:
```bash
docker-compose stop
```

#### Parar e remover o container:
```bash
docker-compose down
```

#### Ver logs em tempo real:
```bash
docker-compose logs -f
```

#### Reconstruir após mudanças no código:
```bash
docker-compose up --build -d
```

## 🌐 Acessar a aplicação

Após iniciar o container, acesse:

- **Aplicação principal**: http://localhost:8000
- **Guia de uso**: http://localhost:8000/guia

## 🔧 Configuração

Certifique-se de que o arquivo `.env` existe na raiz do projeto com as seguintes variáveis:

```
GOOGLE_API_KEY=sua_chave_api
USER=seu_usuario_sei
PASSWORD=sua_senha_sei
ORGAO=CBMMG
```

### 🌐 Configuração de Proxy (PRODEMGE)

A aplicação já está configurada para usar o proxy da PRODEMGE automaticamente:

- **Proxy HTTP/HTTPS**: `http://proxy.prodemge.gov.br:8080`
- Configurado tanto no **build** quanto no **runtime**
- Aplica-se a:
  - ✅ Instalação de pacotes Python (pip)
  - ✅ Download do Google Chrome
  - ✅ Chamadas à API do Google (Gemini)
  - ✅ Requisições HTTP do Selenium

**Não é necessário configurar nada manualmente**, o proxy já está embutido no Docker.

## 📦 Estrutura Docker

- **Dockerfile**: Define a imagem com Python 3.11, Chrome e todas as dependências + configuração de proxy
- **docker-compose.yml**: Orquestra o container com configurações otimizadas + variáveis de proxy
- **.dockerignore**: Ignora arquivos desnecessários no build

## ⚙️ Configurações Especiais

O container está configurado com:
- ✅ Hot-reload ativado (mudanças no código refletem automaticamente)
- ✅ Chrome headless otimizado para containers
- ✅ 2GB de memória compartilhada para Selenium
- ✅ Capacidades SYS_ADMIN para Chrome

## 🐛 Troubleshooting

### Docker não está rodando
```bash
# Abra o Docker Desktop manualmente
```

### Porta 8000 já está em uso
```bash
# Modifique a porta no docker-compose.yml:
ports:
  - "8001:8000"  # Usa porta 8001 no host
```

### Erro ao construir imagem
```bash
# Limpe o cache do Docker e reconstrua
docker-compose down
docker system prune -f
docker-compose up --build -d
```

### Container não inicia
```bash
# Veja os logs para identificar o erro
docker-compose logs
```

## 🔄 Atualizar a aplicação

Após fazer mudanças no código:

1. O hot-reload cuida das mudanças em arquivos Python automaticamente
2. Para mudanças em dependências (requirements.txt):
   ```bash
   docker-compose up --build -d
   ```

## 🛑 Parar completamente

Para parar e remover tudo (container, rede, volumes):
```bash
docker-compose down -v
```

## 📝 Notas

- O código é mapeado como volume, então mudanças são refletidas em tempo real
- O arquivo `.env` não é copiado para a imagem (mais seguro)
- O Chrome roda em modo headless dentro do container
- Logs do Selenium podem ser visualizados com `docker-compose logs -f`
