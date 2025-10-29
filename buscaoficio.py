from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os

def busca_conteudo_oficio(doc_sei: str, navegador) -> str:
    # clicar em Pesquisar
    pesquisa = navegador.find_element(By.ID, "txtPesquisaRapida")
    pesquisa.send_keys(doc_sei)
    pesquisa.send_keys(Keys.ENTER)
    print('pesquisou')

    # mudar o frame
    iframe = navegador.find_element(By.ID, "ifrVisualizacao")
    navegador.switch_to.frame(iframe)
    print('mudou para o frame ifrVisualizacao')
    sleep(0.5)

    # mudar o frame
    iframe = navegador.find_element(By.ID, "ifrArvoreHtml")
    navegador.switch_to.frame(iframe)
    print('mudou para o frame ifrArvoreHtml')
    sleep(0.5)

    # pegar os paragrafos
    paragrafos_tratados = ''
    paragrafos = navegador.find_elements(By.CSS_SELECTOR, "body > p")
    print(f'foram encontrados {len(paragrafos)} paragrafos')
    for paragrafo in paragrafos:
        #print(paragrafo.get_attribute("textContent"))
        if paragrafo.get_attribute("class") == 'Cabeçalho_Rodapé':
            continue
        paragrafos_tratados += paragrafo.get_attribute("textContent") + '\n'
        #print(paragrafo.get_attribute("class")+": "+paragrafo.text)
    #sleep(5)
    #navegador.quit()
    
    print('pegou os paragrafos')
    
    return paragrafos_tratados
