@echo off
echo ========================================
echo  Criador de Oficios SEI - Docker
echo ========================================
echo.

REM Verificar se o Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo [!] Docker nao esta instalado!
    echo [*] Por favor, instale o Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [*] Docker encontrado!
echo.

REM Verificar se a porta 8000 está em uso
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] ATENCAO: Porta 8000 ja esta em uso!
    echo.
    echo [*] Containers Docker em execucao:
    docker ps
    echo.
    echo [?] Deseja parar containers existentes e limpar? (S/N)
    choice /C SN /M "Escolha"
    if errorlevel 2 goto :skipclean
    if errorlevel 1 (
        echo.
        echo [*] Parando containers antigos...
        docker ps -q | ForEach-Object { docker stop $_ }
        echo [*] Removendo containers antigos...
        docker ps -aq | ForEach-Object { docker rm $_ }
        echo [*] Limpando recursos...
        docker system prune -f
        timeout /t 3 /nobreak >nul
    )
)
:skipclean

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo [!] Arquivo .env nao encontrado!
    echo [*] Por favor, crie o arquivo .env com as credenciais necessarias.
    pause
    exit /b 1
)

echo [*] Construindo a imagem Docker...
docker-compose build

if errorlevel 1 (
    echo [!] Erro ao construir a imagem!
    pause
    exit /b 1
)

echo.
echo [*] Iniciando o container...
docker-compose up -d

if errorlevel 1 (
    echo [!] Erro ao iniciar o container!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Aplicacao iniciada com sucesso!
echo ========================================
echo.
echo [*] Aplicacao rodando em: http://localhost:8000
echo [*] Guia disponivel em: http://localhost:8000/guia
echo.
echo [*] Para ver os logs:        docker-compose logs -f
echo [*] Para parar:              docker-compose stop
echo [*] Para parar e remover:    docker-compose down
echo.
echo ========================================

REM Aguardar alguns segundos para garantir que subiu
timeout /t 3 /nobreak >nul

REM Abrir navegador
start http://localhost:8000

pause
