from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os
import json
import requests
from ai_converter import make_response
from buscaoficio import busca_conteudo_oficio
from handle_listas import tranform_text_atribuicao
from dotenv import load_dotenv
import uvicorn
from utils import cria_oficio

load_dotenv()

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados para a requisição
class OficioRequest(BaseModel):
    doc_sei: str
    assunto: str
    destinatario: str
    signatario: str
    graduacao: str
    funcao: str
    processo: str
    # Campos do marcador
    etiqueta: str = "Aguardando Despacho do Major"
    msg: str = ""
    ofreferencia: str = ""
    atribuicao: str = "Maj Rocha"
    # Campo complementar para a IA
    complementar: str = ""
    has_ticket: bool = False


@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/guia")
def guia():
    return FileResponse("guia.html")

@app.get("/style.css")
def get_css():
    return FileResponse("style.css")

@app.get("/script.js")
def get_js():
    return FileResponse("script.js")

@app.get("/dadosmil.json")
def get_dadosmil():
    return FileResponse("dadosmil.json")

def gerar_status(mensagem: str, tipo: str = "info", progresso: int = None):
    """Função auxiliar para gerar mensagens de status"""
    data = {"tipo": tipo, "mensagem": mensagem}
    if progresso is not None:
        data["progresso"] = progresso
    return json.dumps(data) + "\n"

@app.post("/responde_processo")
async def construtor_off(request: OficioRequest):
    
    async def gerar_resposta():
        try:
            yield gerar_status("Iniciando processo...", "info", 0)
            
            # Definição de Variaveis
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless=new')
            
            # Argumentos adicionais para headless funcionar melhor
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            
            # Configurações para evitar detecção de automação
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Preferências adicionais
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            }
            options.add_experimental_option("prefs", prefs)

            servico = Service(ChromeDriverManager().install())
            navegador = webdriver.Chrome(service=servico, options=options)
            navegador.implicitly_wait(10)

            user = os.getenv("USER")
            password = os.getenv("PASSWORD")
            orgao = os.getenv("ORGAO")

            yield gerar_status("Acessando o sistema SEI...", "info", 5)
            
            # acessa o site do SEI
            navegador.get("https://www.sei.mg.gov.br/")
            
            # Não precisa de maximize_window no headless (já definido no window-size)

            # inserir o meu usuário
            navegador.find_element(By.ID, "txtUsuario").send_keys(user)
            sleep(0.5)

            # inserir minha senha
            navegador.find_element(By.ID, "pwdSenha").send_keys(password)

            # inserir o orgao
            select_element = navegador.find_element(By.ID, "selOrgao")
            select = Select(select_element)
            select.select_by_visible_text(orgao)

            # clicar no botão acessar
            navegador.find_element(By.ID, "Acessar").click()

            yield gerar_status("Login realizado com sucesso!", "success", 15)
            yield gerar_status("Buscando conteúdo do ofício...", "info", 20)

            # buscar o conteudo do oficio
            pergunta_ia = busca_conteudo_oficio(request.doc_sei, navegador)
            
            yield gerar_status("Conteúdo encontrado! Gerando resposta com IA...", "info", 35)

            # passa o prompt para a ia
            resposta_ia = make_response(pergunta_ia, request.complementar)

            yield gerar_status("Resposta gerada pela IA!", "success", 50)
            yield gerar_status("Criando ofício...", "info", 55)

            # criar o oficio
            conteudo_oficio = cria_oficio(request.assunto, request.destinatario, request.signatario, request.graduacao, request.funcao, resposta_ia, request.ofreferencia)

            yield gerar_status("Mudando para frame padrão...", "info", 60)
            
            # voltar para o frame padrão
            navegador.switch_to.default_content()

            # clicar em Pesquisar
            pesquisa = navegador.find_element(By.ID, "txtPesquisaRapida")
            pesquisa.send_keys(request.processo)
            pesquisa.send_keys(Keys.ENTER)

            yield gerar_status(f"Processo {request.processo} encontrado!", "success", 65)

            sleep(1)
            # mudar o frame
            iframe = navegador.find_element(By.ID, "ifrVisualizacao")
            navegador.switch_to.frame(iframe)
            sleep(1)

            yield gerar_status("Incluindo documento...", "info", 70)

            # cliar em Incluir Documento
            navegador.execute_script('document.querySelector("#divArvoreAcoes > a:nth-child(1) > img").click()')

            yield gerar_status("Documento incluído!", "success", 75)

            # clicar em Ofício
            sleep(1)  # Aumentado para headless
            navegador.execute_script("document.querySelectorAll('a').forEach(a => a.textContent.trim() === 'Ofício' && a.click());")

            yield gerar_status("Tipo Ofício selecionado!", "info", 78)

            sleep(2)  # Aumentado para headless
            # clicar em Público
            navegador.execute_script('document.querySelector("#optPublico").click()')
            sleep(1)  # Aumentado para headless

            # clicar em Salvar
            navegador.execute_script('document.querySelector("#btnSalvar").click()')
            
            yield gerar_status("Ofício salvo!", "success", 82)
            
            sleep(12)  # Aumentado para headless - aguardar nova janela abrir

            # mudar a janela - esperar até ter 2 janelas
            wait = WebDriverWait(navegador, 20)
            wait.until(lambda d: len(d.window_handles) > 1)
            
            janela2 = navegador.window_handles[1]
            navegador.switch_to.window(janela2)
            
            sleep(2)  # Aguardar janela carregar completamente

            yield gerar_status("Inserindo conteúdo no editor...", "info", 85)

            # mudar o iframe - aguardar estar presente
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#cke_4_contents > iframe")))
            navegador.switch_to.frame(iframe)
            
            sleep(1)  # Aguardar iframe carregar
            
            navegador.execute_script(f"document.body.innerHTML = `{conteudo_oficio}`")
            
            sleep(1)  # Aguardar conteúdo ser inserido
            
            yield gerar_status("Conteúdo inserido no ofício!", "success", 90)

            # salvar o documento
            navegador.switch_to.default_content()
            sleep(2)
            
            # Clicar no botão salvar com wait
            btn_salvar = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[1]/div[1]/div/div/span[2]/span[1]/span[3]/a")))
            navegador.execute_script("arguments[0].click();", btn_salvar)
            
            yield gerar_status("Salvando documento...", "info", 95)
            
            sleep(3)  # Aumentado para headless
            navegador.close()
            
            yield gerar_status("Documento salvo! Iniciando marcação...", "success", 96)
            
            # ============= INÍCIO DA MARCAÇÃO (marcador.py) =============
            
            # Voltar para a janela principal
            navegador.switch_to.window(navegador.window_handles[0])
            navegador.switch_to.default_content()
            
            sleep(1)  # Aguardar foco na janela
            
            yield gerar_status("Pesquisando processo para marcação...", "info", 97)
            
            # Pesquisar o processo novamente
            campo_pesquisa = wait.until(EC.presence_of_element_located((By.ID, "txtPesquisaRapida")))
            campo_pesquisa.clear()
            sleep(0.5)
            campo_pesquisa.send_keys(request.processo)
            campo_pesquisa.send_keys(Keys.ENTER)
            
            sleep(2)  # Aumentado para headless
            
            # Mudar para o frame de visualização
            wait = WebDriverWait(navegador, 15)  # Aumentado timeout
            frame_2 = wait.until(EC.presence_of_element_located((By.ID, 'ifrVisualizacao')))
            navegador.switch_to.frame(frame_2)
            
            sleep(2)  # Aguardar frame carregar
            
            yield gerar_status("Adicionando anotação...", "info", 98)
            
            sleep(3)  # Aumentado para headless - Aguardar carregamento da página
            
            # Clicar em adicionar anotação - tentar diferentes métodos
            try:
                # Método 1: Procurar link com texto contendo "marcador_gerenciar"
                links = navegador.find_elements(By.CSS_SELECTOR, '#divArvoreAcoes a')
                link_encontrado = False
                for link in links:
                    href = link.get_attribute('href') or ''
                    if 'marcador_gerenciar' in href:
                        navegador.execute_script("arguments[0].click();", link)
                        link_encontrado = True
                        break
                
                if not link_encontrado:
                    raise Exception("Link marcador_gerenciar não encontrado")
            except:
                try:
                    # Método 2: Aguardar e clicar via JavaScript
                    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="divArvoreAcoes"]/a[24]')))
                    navegador.execute_script('document.querySelector("#divArvoreAcoes > a:nth-child(24)").click()')
                except:
                    # Método 3: Clicar diretamente no elemento
                    try:
                        btn_anotacao = navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[24]')
                        navegador.execute_script("arguments[0].click();", btn_anotacao)
                    except:
                        # Método 4: Link pelo texto/título
                        links = navegador.find_elements(By.CSS_SELECTOR, '#divArvoreAcoes a')
                        for link in links:
                            if 'Anotação' in link.get_attribute('title') or 'Anotar' in link.get_attribute('title'):
                                navegador.execute_script("arguments[0].click();", link)
                                break
                        
            sleep(1)  # Aumentado para headless
            if request.has_ticket:
                
                navegador.execute_script('document.querySelector("#btnAdicionar").click()')
            
            sleep(2)  # Aumentado para headless
            
            # Clicar no seletor de marcador
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#selMarcador > div > span')))
                sleep(1)  # Aguardar antes de clicar
                navegador.execute_script('document.querySelector("#selMarcador > div > span").click()')
            except:
                # Tentar método alternativo
                navegador.find_element(By.CSS_SELECTOR, '#selMarcador').click()
            
            sleep(2)  # Aumentado para headless
            
            sleep(2)  # Aumentado para headless
            
            # Aguardar que as opções estejam visíveis
            opcoes = WebDriverWait(navegador, 15).until(  # Aumentado timeout
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a.dd-option"))
            )
            
            sleep(1)  # Aumentado para headless
            
            # Iterar sobre as opções e clicar na etiqueta correta
            etiqueta_encontrada = False
            for opcao in opcoes:
                texto = opcao.text.strip()
                if texto == request.etiqueta:
                    sleep(0.5)  # Pequeno delay antes de clicar
                    navegador.execute_script("arguments[0].click();", opcao)
                    etiqueta_encontrada = True
                    break
            
            if not etiqueta_encontrada:
                yield gerar_status(f"⚠️ Etiqueta '{request.etiqueta}' não encontrada, usando primeira opção", "warning", 98)
                navegador.execute_script("arguments[0].click();", opcoes[0])
            
            sleep(1)  # Aumentado para headless
            
            # Inserir a mensagem
            textarea = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txaTexto"]')))
            sleep(0.5)
            textarea.clear()
            textarea.send_keys(request.msg)
            
            sleep(1)  # Aumentado para headless
            
            # Salvar anotação
            btn_salvar = navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]')
            navegador.execute_script("arguments[0].click();", btn_salvar)
            
            sleep(3)  # Aumentado para headless - Aguardar salvamento
            
            yield gerar_status("Anotação adicionada! Atribuindo processo...", "success", 99)
            
            # Atualizar a página
            navegador.refresh()
            sleep(3)  # Aumentado para headless
            
            # Mudar para o frame correto
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ifrVisualizacao')))
            
            sleep(2)  # Aumentado para headless
            
            # Clicar em atribuir processo
            try:
                btn_atribuir = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]')))
                sleep(0.5)
                navegador.execute_script("arguments[0].click();", btn_atribuir)
            except:
                # Tentar encontrar pelo título
                links = navegador.find_elements(By.CSS_SELECTOR, '#divArvoreAcoes a')
                for link in links:
                    titulo = link.get_attribute('title')
                    if titulo and 'Atribuir' in titulo:
                        navegador.execute_script("arguments[0].click();", link)
                        break
            
            sleep(2)  # Aumentado para headless
            
            # Converter atribuição para o formato correto
            atribuicao_formatada = tranform_text_atribuicao(request.atribuicao)
            
            yield gerar_status(f"Atribuindo para: {atribuicao_formatada}", "info", 99)
            
            # Aguardar o select estar presente
            wait.until(EC.presence_of_element_located((By.ID, "selAtribuicao")))
            sleep(1)  # Aguardar select carregar completamente
            
            # Script JavaScript para selecionar a atribuição
            script = f"""
            var atribuicao = "{atribuicao_formatada}";
            var selectElement = document.querySelector("#selAtribuicao");
            if (selectElement) {{
                for (var i = 0; i < selectElement.options.length; i++) {{
                    if (selectElement.options[i].text === atribuicao) {{
                        selectElement.selectedIndex = i;
                        selectElement.dispatchEvent(new Event('change'));
                        return true;
                    }}
                }}
            }}
            return false;
            """
            resultado = navegador.execute_script(script)
            
            if not resultado:
                yield gerar_status(f"⚠️ Atribuição '{atribuicao_formatada}' não encontrada", "warning", 99)
            
            sleep(1)  # Aumentado para headless
            
            # Salvar atribuição
            btn_salvar_atrib = navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]')
            navegador.execute_script("arguments[0].click();", btn_salvar_atrib)
            
            sleep(3)  # Aumentado para headless
            
            yield gerar_status("✅ SUCESSO COMPLETO! Ofício criado, marcado e atribuído!", "success", 100)
            
            # ============= FIM DA MARCAÇÃO =============
            
            
        except Exception as e:
            yield gerar_status(f"❌ ERRO: {str(e)}", "error")
            try:
                navegador.quit()
            except:
                pass
    
    return StreamingResponse(gerar_resposta(), media_type="application/x-ndjson")


# ============================================
# TRELLO MODULE
# ============================================

class TrelloCardRequest(BaseModel):
    board_name: str
    label_name: str
    label_color: str
    auto_title: bool
    card_title: str = ""
    card_description: str
    list_name: str
    due_date: Optional[str] = None
    use_ai: bool = True  # Sempre usar IA por padrão


@app.get("/trello.js")
def get_trello_js():
    return FileResponse("trello.js")


@app.post("/criar-card-trello")
async def criar_card_trello(request: Request):
    """
    Endpoint para criar um card no Trello com formatação via IA
    """
    import requests
    
    # Log do payload raw para debug
    try:
        body = await request.json()
        print("\n=== DEBUG: Payload RAW recebido ===")
        print(json.dumps(body, indent=2))
    except Exception as e:
        print(f"\n=== DEBUG: Erro ao ler payload: {e} ===")
        return {
            "success": False,
            "error": f"Erro ao processar payload: {str(e)}"
        }
    
    # Validar payload com Pydantic
    try:
        validated_request = TrelloCardRequest(**body)
    except Exception as e:
        print(f"\n=== DEBUG: Erro de validação Pydantic ===")
        print(f"Erro: {str(e)}")
        return {
            "success": False,
            "error": f"Dados inválidos: {str(e)}"
        }
    
    print("\n=== DEBUG: Iniciando criar_card_trello ===")
    print(f"use_ai: {validated_request.use_ai}")
    print(f"auto_title: {validated_request.auto_title}")
    print(f"card_title: {validated_request.card_title}")
    print(f"card_description: {validated_request.card_description}")
    
    # Credenciais do Trello
    TRELLO_API_KEY = os.getenv('API_KEY')
    TRELLO_TOKEN = os.getenv('TOKEN')
    TRELLO_BASE_URL = "https://api.trello.com/1"
    
    def get_trello_auth():
        return {'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN}
    
    try:
        card_title = validated_request.card_title
        card_desc = validated_request.card_description
        
        # Se use_ai estiver ativo, processar com OpenAI
        if validated_request.use_ai:
            print("\n=== DEBUG: use_ai está ATIVO, processando com OpenAI ===")
            
            import openai
            
            # Configurar cliente OpenAI
            client = openai.Client()
            
            # Prompt para formatação da descrição
            prompt_descricao = f"""Você é um Product Owner + Arquiteto de Software do CBMMG e sua tarefa é transformar uma única entrada chamada {{DESCRICAO}} em um CARD de Trello completo, didático e tecnicamente detalhado, escrito em português do Brasil.

REGRAS IMPORTANTES
1) Você receberá SOMENTE {{DESCRICAO}}. Não faça perguntas de volta.
2) Você deve inferir e completar o que faltar com suposições plausíveis, mas deixe claro quando algo for suposição usando o marcador: "⚠️ Suposição:".
3) O resultado deve vir em formato único, pronto para colar no Trello, com:
   - Linha 1: "Título: <...>"
   - Em seguida: "Descrição:" e o corpo completo.
4) Não use tabelas. Use seções e listas curtas, com emojis discretos (no máximo 1 por seção).
5) Deve ficar suficientemente detalhado para orientar um time a construir o sistema.

ESTRUTURA OBRIGATÓRIA DO CARD
Título: <nome do projeto + objetivo em 8–14 palavras>

Descrição:
🧩 Visão Geral
- Explique o propósito do sistema, o problema que resolve e para quem.
- Contexto operacional (quando aplicável: CBMMG, unidades, integrações, etc.).

🎯 Objetivos e Resultados Esperados
- Liste 3 a 7 resultados mensuráveis (ex: reduzir tempo, centralizar dados, auditoria, transparência, etc.).

👥 Perfis de Usuário e Permissões
- Defina perfis (ex: admin, gestor, operador, auditor, API client).
- Regras de acesso (RBAC) e trilha de auditoria.

📦 Escopo Funcional (MVP)
- Liste funcionalidades mínimas em bullets, bem específicas.
- Inclua entradas/saídas, telas e fluxos principais.
- Se houver dados externos, descreva como entram.

🧱 Requisitos Não Funcionais
- Segurança (JWT/OAuth, rate-limit, logs, LGPD quando aplicável)
- Performance (metas de tempo de resposta, volume esperado)
- Disponibilidade/Resiliência (retry, fila, fallback)
- Observabilidade (logs, métricas, alertas)

🛠️ Arquitetura Proposta
- Componentes: frontend, backend, banco, integrações, filas/cache se necessário.
- Padrões: REST, Webhook, Worker, Scheduler, etc.
- Ambientes: dev/homolog/prod e diferenças (ex: SQLite dev vs Postgres prod).

🗃️ Modelo de Dados (alto nível)
- Entidades principais (ex: Usuario, Permissao, Evento, Registro, etc.)
- Relacionamentos e chaves relevantes.

🔌 Integrações e Dependências
- Sistemas externos, autenticação, chaves, whitelists de IP, etc.
- O que é bloqueador se faltar (credenciais, tabelas auxiliares, acesso).

🔒 Segurança e Conformidade
- Controles mínimos: criptografia em trânsito, segredo em vault/.env, auditoria.
- Proteções: throttling, bloqueio por IP, validação de payload, etc.

✅ Critérios de Aceite
- 6 a 10 critérios objetivos (Given/When/Then ou bullets verificáveis).

🧪 Plano de Testes (mínimo)
- Unitários, integração, E2E (se houver UI), carga (se aplicável).

🚀 Próximos Passos (Backlog sugerido)
- 5 a 10 itens priorizados (MVP → evolução).

ENTRADA
{validated_request.card_description}

SAÍDA
Gere APENAS o card no formato definido, sem comentários extras, sem saudações, sem perguntas.
"""
            
            print("\n=== DEBUG: Chamando OpenAI API ===")
            print(f"Modelo: gpt-3.5-turbo-0125")
            
            # Gerar descrição formatada usando OpenAI
            mensagens = [
                {"role": "user", "content": prompt_descricao}
            ]
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=mensagens,
                max_tokens=2000,
                temperature=0.7
            )
            
            card_content = response.choices[0].message.content
            print("\n=== DEBUG: Resposta da OpenAI recebida ===")
            print(f"Tamanho da resposta: {len(card_content)} caracteres")
            print(f"Primeiros 200 chars: {card_content[:200]}...")
            
            # Extrair título e descrição separados
            card_desc = card_content
            
            # Se auto_title estiver ativo, extrair o título da resposta da IA
            if validated_request.auto_title:
                print("\n=== DEBUG: auto_title está ATIVO, extraindo título ===")
                lines = card_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('Título:'):
                        card_title = line.replace('Título:', '').strip()
                        print(f"DEBUG: Título extraído: {card_title}")
                        # Remover linha do título da descrição
                        card_desc = '\n'.join(lines[i+1:]).strip()
                        if card_desc.startswith('Descrição:'):
                            card_desc = card_desc.replace('Descrição:', '', 1).strip()
                        break
            
            print(f"\n=== DEBUG: Título final: {card_title} ===")
            print(f"=== DEBUG: Descrição final (primeiros 200 chars): {card_desc[:200]}... ===")
        else:
            print("\n=== DEBUG: use_ai está DESATIVADO, usando texto original ===")
        
        print(f"\n=== DEBUG: Título que será enviado ao Trello: {card_title} ===")
        print(f"=== DEBUG: Descrição que será enviada (primeiros 200 chars): {card_desc[:200] if len(card_desc) > 200 else card_desc} ===")

        
        # ============= INTEGRAÇÃO COM TRELLO =============
        
        # 1. Buscar board pelo nome
        boards_url = f"{TRELLO_BASE_URL}/members/me/boards"
        boards_response = requests.get(boards_url, params={**get_trello_auth(), 'fields': 'name,id'})
        boards = boards_response.json()
        
        board_id = None
        for board in boards:
            if board['name'].lower() == validated_request.board_name.lower():
                board_id = board['id']
                break
        
        if not board_id:
            return {"success": False, "error": f"Board '{validated_request.board_name}' não encontrado"}
        
        # 2. Buscar lista pelo nome
        lists_url = f"{TRELLO_BASE_URL}/boards/{board_id}/lists"
        lists_response = requests.get(lists_url, params={**get_trello_auth(), 'fields': 'name,id'})
        lists = lists_response.json()
        
        list_id = None
        for lst in lists:
            if lst['name'].lower() == validated_request.list_name.lower():
                list_id = lst['id']
                break
        
        if not list_id:
            return {"success": False, "error": f"Lista '{validated_request.list_name}' não encontrada no board"}
        
        # 3. Buscar ou criar label
        labels_url = f"{TRELLO_BASE_URL}/boards/{board_id}/labels"
        labels_response = requests.get(labels_url, params=get_trello_auth())
        labels = labels_response.json()
        
        label_id = None
        for label in labels:
            if label.get('name', '').lower() == validated_request.label_name.lower():
                label_id = label['id']
                break
        
        # Se label não existe, criar um novo
        if not label_id:
            create_label_url = f"{TRELLO_BASE_URL}/labels"
            label_params = {
                **get_trello_auth(),
                'name': validated_request.label_name,
                'color': validated_request.label_color,
                'idBoard': board_id
            }
            label_response = requests.post(create_label_url, params=label_params)
            if label_response.status_code == 200:
                label_id = label_response.json()['id']
        
        # 4. Criar o card
        card_url = f"{TRELLO_BASE_URL}/cards"
        card_params = {
            **get_trello_auth(),
            'idList': list_id,
            'name': card_title,
            'desc': card_desc,
            'pos': 'top'
        }
        
        print(f"\n=== DEBUG: Criando card no Trello ===")
        print(f"URL: {card_url}")
        print(f"Nome do card: {card_title}")
        print(f"Descrição (primeiros 200 chars): {card_desc[:200] if len(card_desc) > 200 else card_desc}")
        
        # Adicionar label se encontrado/criado
        if label_id:
            card_params['idLabels'] = label_id
            print(f"DEBUG: Label ID adicionado: {label_id}")
        
        # Adicionar data de vencimento se fornecida
        if validated_request.due_date:
            card_params['due'] = validated_request.due_date
            print(f"DEBUG: Data de vencimento: {validated_request.due_date}")
        
        card_response = requests.post(card_url, params=card_params)
        print(f"\n=== DEBUG: Status da resposta do Trello: {card_response.status_code} ===")

        
        if card_response.status_code == 200:
            created_card = card_response.json()
            print(f"\n=== DEBUG: Card criado com SUCESSO! ===")
            print(f"Card ID: {created_card['id']}")
            print(f"Card URL: {created_card['url']}")
            return {
                "success": True,
                "message": "Card criado com sucesso!",
                "card_title": card_title,
                "card_id": created_card['id'],
                "card_url": created_card['url']
            }
        else:
            print(f"\n=== DEBUG: ERRO ao criar card ===")
            print(f"Status: {card_response.status_code}")
            print(f"Resposta: {card_response.text}")
            return {
                "success": False,
                "error": f"Erro ao criar card: {card_response.text}"
            }
        
    except Exception as e:
        import traceback
        print(f"\n=== DEBUG: EXCEÇÃO capturada ===")
        print(f"Erro: {str(e)}")
        print(f"Traceback completo:")
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Erro ao criar card: {str(e)}"
        }
    
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)