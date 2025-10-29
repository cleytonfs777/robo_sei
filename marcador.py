from datetime import datetime
from selenium.common.exceptions import TimeoutException  # Importar TimeoutException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os
from handle_listas import tranform_text_atribuicao

from dotenv import load_dotenv
load_dotenv()


def query(numSei="1400.01.0074829/2025-05", etiqueta="Aguardando Despacho do Major", msg="Atribuição do sei certo", atribuicao="Maj Giovanny"):
    

    atribuicao = tranform_text_atribuicao(atribuicao)

    # Define variáveis globaiso
    adicionarBotao = False

    USER_ACCOUNT = os.getenv("USER")
    PASS_ACCOUNT = os.getenv("PASSWORD")
    UNID_ACCOUNT = os.getenv("ORGAO")

    try:

        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # Defina o tamanho da janela
        options.add_argument("--window-size=1920,1080")

        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=options)
        navegador.implicitly_wait(10)

        url = "https://www.sei.mg.gov.br"
        navegador.get(url)

        print(USER_ACCOUNT)
        
        print("Acessando o SEI...")

        # Insere a credencial de login
        navegador.find_element(By.ID, "txtUsuario").send_keys(USER_ACCOUNT)

        # Insere a Senha de login
        navegador.find_element(By.ID, "pwdSenha").send_keys(PASS_ACCOUNT)

        # Realiza o select cujo texto é "Selecione o Orgão"
        select_element = navegador.find_element(
            By.ID, "selOrgao"
        )
        # Crie um objeto Select com o elemento encontrado
        select = Select(select_element)

        # Selecione a opção pelo texto visível
        select.select_by_visible_text(UNID_ACCOUNT)

        # Clique no botão Acessar
        navegador.find_element(By.ID, "Acessar").click()

        ################# SEGUNDA PARTE #################

        print("Login realizado com sucesso. Aguardando busca...")

        # Insira no campo perquisa de id=txtPesquisaRapida o valor que está na variavel numSei
        navegador.find_element(By.ID, "txtPesquisaRapida").send_keys(numSei)

        # Tecle Enter
        navegador.find_element(
            By.ID, "txtPesquisaRapida").send_keys(Keys.ENTER)

        print("Iniciadno pesquisa...")
        
        # Aguarde até que o primeiro frame esteja presente e mude para ele
        wait = WebDriverWait(navegador, 10)

        # Aguarde até que o segundo frame esteja presente e mude para ele
        frame_2 = wait.until(EC.presence_of_element_located(
            (By.ID, 'ifrVisualizacao')))
        navegador.switch_to.frame(frame_2)
        
        print("Mudou o frame")

        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[22]').click()

        if adicionarBotao:
            navegador.find_element(
                By.CSS_SELECTOR, '#btnAdicionar').click()

        navegador.find_element(
            By.CSS_SELECTOR, '#selMarcador > div > span').click()

        # Aguardar que as opções estejam visíveis
        opcoes = WebDriverWait(navegador, 10).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "a.dd-option"))
        )
        
        print(f"Numero de opções localizadas: {len(opcoes)}")
        
        print("Iniciando iteração")
        print(f"Etiqueta é: {etiqueta}")

        # Iterar sobre as opções e clicar naquela que corresponde ao texto alvo
        for opcao in opcoes:
            texto = opcao.text.strip()
            print(f"Opção: {texto}")
            print(f"Etiqueta: {etiqueta}")
            if texto == etiqueta:
                opcao.click()
                break

        # Insere o conteudo de msg no campo de mensagens //*[@id="txaTexto"]
        navegador.find_element(By.XPATH, '//*[@id="txaTexto"]').send_keys(msg)

        # Clica atraves do XPATH no botão //*[@id="sbmSalvar"]
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()

        print("Despacho realizado com sucesso. Aguardando atribuição...")

        # Atualiza a pagina
        navegador.refresh()

        navegador.switch_to.frame(1)

        # Faz um click no botao XPATH //*[@id="divArvoreAcoes"]/a[8]
        navegador.find_element(
            By.XPATH, '//*[@id="divArvoreAcoes"]/a[8]').click()

        # Script JavaScript para selecionar a opção pelo texto
        script = f"""
        var atribuicao = "{atribuicao}";
        var selectElement = document.querySelector("#selAtribuicao");
        for (var i = 0; i < selectElement.options.length; i++) {{
            if (selectElement.options[i].text === atribuicao) {{
                selectElement.selectedIndex = i;
                selectElement.dispatchEvent(new Event('change'));
                break;
            }}
        }}
        """
        # Executar o script
        navegador.execute_script(script)

        # Clica no botao de XPATH //*[@id="sbmSalvar"]
        navegador.find_element(By.XPATH, '//*[@id="sbmSalvar"]').click()

        sleep(1)


    except Exception as e:


        print(f"Erro: {e}")


if __name__ == "__main__":
    query()
