@echo off
echo ========================================
echo  Limpeza de Containers Docker
echo ========================================
echo.

echo [*] Parando container PHP antigo na porta 8000...
docker stop 5a2074a246d3 2>nul
if %errorlevel% equ 0 (
    echo [OK] Container PHP parado com sucesso!
) else (
    echo [!] Container PHP ja estava parado ou nao existe.
)

echo.
echo [*] Removendo container PHP antigo...
docker rm 5a2074a246d3 2>nul
if %errorlevel% equ 0 (
    echo [OK] Container PHP removido com sucesso!
) else (
    echo [!] Container PHP ja foi removido ou nao existe.
)

echo.
echo [*] Verificando porta 8000...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo [!] Porta 8000 ainda em uso. Aguarde alguns segundos...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Porta 8000 livre!
)

echo.
echo [*] Limpando recursos nao utilizados do Docker...
docker system prune -f

echo.
echo ========================================
echo  Limpeza concluida!
echo ========================================
echo.
echo [*] A porta 8000 esta livre para uso.
echo [*] Agora voce pode executar: start-docker.bat
echo.

pause
