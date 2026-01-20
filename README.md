# �️ SDTS-3 Tools - Sistema de Ferramentas Integradas

Sistema modular de ferramentas para automação de processos administrativos do CBMMG.

## 📦 Módulos

### 🔥 Criador de Ofícios SEI
Sistema automatizado de criação de ofícios no SEI com inteligência artificial.
- Interface web moderna e responsiva
- Integração com Google Generative AI (Gemini)
- Automação completa do processo no SEI
- Feedback em tempo real do progresso
- Suporte a proxy corporativo
- Geração automática de respostas com IA

### 📋 Gerador de Trello
Módulo para geração automática de cards do Trello com formatação inteligente via IA.

**Funcionalidades:**
- 🏷️ Sistema de gerenciamento de labels (criar, editar, excluir)
- 🤖 Geração automática de títulos com IA
- 📝 Formatação automática de descrições seguindo padrão de Product Owner
- 🎯 Estruturação completa do card (visão geral, objetivos, arquitetura, etc.)
- 📅 Suporte a datas de vencimento
- 💾 Armazenamento local dos labels configurados
- 🎨 10 cores de labels disponíveis

**Status:** ✅ Funcional (integração com API do Trello pendente)

## 📋 Funcionalidades Gerais

- ✅ Interface com menu lateral navegável
- ✅ Suporte a múltiplos módulos
- ✅ Design responsivo (mobile-friendly)
- ✅ Integração com APIs externas

## 🚀 Como Usar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Credenciais do SEI
USER=seu_usuario_sei
PASSWORD=sua_senha_sei
ORGAO=seu_orgao

# API Key do Google Generative AI
GOOGLE_API_KEY=sua_chave_api_google

# API do Trello (opcional - para módulo Trello)
TRELLO_API_KEY=sua_chave_api_trello
TRELLO_TOKEN=seu_token_trello
```

**Como obter credenciais do Trello:**
1. Acesse: https://trello.com/power-ups/admin
2. Crie um novo Power-Up para obter sua API Key
3. Gere um token de acesso com as permissões necessárias

### 3. Iniciar o Servidor

```bash
python app.py
```

O servidor será iniciado em `http://localhost:8000`

### 4. Acessar a Interface Web

Abra seu navegador e acesse:
```
http://localhost:8000
```

## 📝 Preenchimento do Formulário

Preencha os seguintes campos:

1. **Documento SEI**: Número do documento que contém o ofício a ser respondido
2. **Número do Processo**: Número completo do processo SEI
3. **Assunto**: Assunto do ofício de resposta
4. **Destinatário**: Nome e cargo do destinatário
5. **Signatário**: Nome do signatário
6. **Graduação**: Graduação do signatário
7. **Função**: Função do signatário

## 🎯 Fluxo de Processamento

1. **Acesso ao SEI**: Sistema faz login automaticamente
2. **Busca do Documento**: Localiza e extrai o conteúdo do ofício original
3. **Geração com IA**: Utiliza o Gemini para criar uma resposta adequada
4. **Criação do Ofício**: Gera o HTML do ofício formatado
5. **Inclusão no Processo**: Adiciona o ofício no processo SEI
6. **Finalização**: Salva e fecha o documento

## 🔧 Arquitetura

### Backend (FastAPI)
- `app.py`: API principal com endpoints
- `ai_converter.py`: Integração com Google Gemini AI
- `buscaoficio.py`: Extração de conteúdo do SEI
- `utils.py`: Funções auxiliares para criação de ofícios

### Frontend
- `index.html`: Estrutura da página
- `style.css`: Estilos modernos e responsivos
- `script.js`: Lógica de interação e requisições

## 📦 Dependências

```
numpy
pandas
google-generativeai
python-dotenv
selenium
webdriver-manager
fastapi
uvicorn
httpx
```

## 🔒 Segurança

- ✅ Uso de variáveis de ambiente para credenciais
- ✅ Execução headless do navegador
- ✅ Suporte a proxy corporativo
- ✅ CORS configurado para desenvolvimento

## 🎨 Interface

A interface moderna conta com:
- Design gradiente atrativo
- Feedback visual em tempo real
- Barra de progresso animada
- Mensagens coloridas por tipo (info, success, error, warning)
- Layout responsivo para mobile
- Ícones intuitivos

## 🐛 Troubleshooting

### Erro de Proxy
Se houver erro de conexão, verifique se o proxy está configurado corretamente em `ai_converter.py`:
```python
os.environ['HTTP_PROXY'] = 'http://proxy.prodemge.gov.br:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.prodemge.gov.br:8080'
```

### Erro de ChromeDriver
O sistema baixa automaticamente o ChromeDriver. Se houver erro:
```bash
pip install --upgrade webdriver-manager
```

### Erro de API Key
Verifique se a `GOOGLE_API_KEY` está configurada corretamente no arquivo `.env`

## 📄 Licença

© 2025 CBMMG - Corpo de Bombeiros Militar de Minas Gerais

## 👨‍💻 Desenvolvedor

Sistema desenvolvido para automatizar a criação de ofícios no SEI.
