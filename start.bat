@echo off
echo ========================================
echo  Criador de Oficios SEI - Iniciando...
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\" (
    echo [!] Ambiente virtual nao encontrado!
    echo [*] Criando ambiente virtual...
    python -m venv venv
    echo [OK] Ambiente virtual criado!
)

REM Ativar ambiente virtual
echo [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verificar se o .env existe
if not exist ".env" (
    echo.
    echo [!] Arquivo .env nao encontrado!
    echo [!] Por favor, crie um arquivo .env baseado no .env.example
    echo [!] Configure suas credenciais antes de continuar.
    echo.
    pause
    exit /b 1
)

REM Instalar dependencias
echo [*] Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo  Servidor iniciando em http://localhost:8000
echo ========================================
echo.

REM Iniciar o servidor
python app.py

pause
