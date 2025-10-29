from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from buscaoficio import busca_conteudo_oficio
from ai_converter import make_response

# importação de módulos criados
from utils import cria_oficio

app = FastAPI()

load_dotenv()

@app.get("/")
def home():
    return {"message": "API de respostas de processos do SEI"}

@app.post("/responde_processo")
def responde_processo(assunto="Meu assunto Padrão", destinatario="Meu assunto Padrão", signatario="STELLA COELI FLORI", graduacao="CEL BM", funcao="DIRETORA DE LOGISTICA E FINANCAS", processo= "1400.01.0074829/2025-05", doc_sei = '126086248', adicional=""):
    try:
        
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')

        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=options)
        navegador.implicitly_wait(10) # espera 10 segundos para todo comando

        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        orgao = os.getenv("ORGAO")
        
        # acessa o site do SEI
        navegador.get("https://www.sei.mg.gov.br/")

        # maximizar janela
        navegador.maximize_window()

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
        
        print('acessou')

        # buscar o conteudo do oficio
        pergunta_ia = busca_conteudo_oficio(doc_sei, navegador)
        print(pergunta_ia)
        
        # passa o prompt para a ia
        resposta_ia = make_response(pergunta_ia, adicional)

        # criar o oficio
        conteudo_oficio = cria_oficio(assunto, destinatario, signatario, graduacao, funcao, resposta_ia)
        print(conteudo_oficio)
        
        print('tentando mudar para o frame padrão')
        # voltar para o frame padrão
        navegador.switch_to.default_content()
    
        # clicar em Pesquisar
        pesquisa = navegador.find_element(By.ID, "txtPesquisaRapida")
        pesquisa.send_keys(processo)
        pesquisa.send_keys(Keys.ENTER)
        
        print('pesquisou o processo')
        

        # mudar o frame
        iframe = navegador.find_element(By.ID, "ifrVisualizacao")
        navegador.switch_to.frame(iframe)
        sleep(1)
        
        print('mudou o frame')

        # cliar em Incluir Documento
        navegador.execute_script('document.querySelector("#divArvoreAcoes > a:nth-child(1) > img").click()')
        #navegador.find_element(By.XPATH, '//*[@id="divArvoreAcoes"]/a[1]').click()
        
        print('incluiu documento')

        # inserir o texto 'Oficio' na caixa de pesquisa
        # pesquisa2 = navegador.find_element(By.ID, "txtFiltro").send_keys("Ofício")

        # clicar em Ofício
        #navegador.find_element(By.CSS_SELECTOR, "#tblSeries > tbody > tr:nth-child(52) > td > a.ancoraOpcao").click()
        #navegador.find_element(By.XPATH, "//a[text()='Ofício']").click()
        navegador.execute_script('document.querySelector("#tblSeries > tbody > tr:nth-child(53) > td > a.ancoraOpcao").click()')
        
        print('clicou em oficio')

        # clicar em Público
        #navegador.find_element(By.CSS_SELECTOR, "#divOptPublico > div > label").click()
        navegador.execute_script('document.querySelector("#optPublico").click()')
        sleep(0.5)

        # clicar em Salvar
        #navegador.find_element(By.ID, "btnSalvar").click()
        navegador.execute_script('document.querySelector("#btnSalvar").click()')
        print('salvou o oficio')
        sleep(10)

        # mudar a janela
        janela2 = navegador.window_handles[1]
        navegador.switch_to.window(janela2)

        # maximizar janela
        #navegador.maximize_window()

        # mudar o iframe
        print('tentando mudar o frame do editor de texto')
        iframe = navegador.find_element(By.CSS_SELECTOR, "#cke_4_contents > iframe")
        navegador.switch_to.frame(iframe)
        navegador.execute_script(f"document.body.innerHTML = `{conteudo_oficio}`")
        print('inseriu o texto no oficio')

        # salvar o documento
        navegador.switch_to.default_content()
        sleep(2)
        navegador.find_element(By.XPATH, "/html/body/form/div[1]/div[1]/div/div/span[2]/span[1]/span[3]/a").click()
        print('clicou em salvar o documento')
        sleep(2)
        navegador.close()
        print('fechou o navegador')
        print('SUCESSO!!!')
        
        #fechar o navegador
        navegador.quit()
        return {"status": "success", "message": "Ofício criado com sucesso!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)