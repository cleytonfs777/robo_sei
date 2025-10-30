# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

def make_response(prompt: str, prompt_master="") -> str:
  print('entrou make_response')
  GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
  
  # Configurar proxy como variáveis de ambiente
  os.environ['HTTP_PROXY'] = 'http://proxy.prodemge.gov.br:8080'
  os.environ['HTTPS_PROXY'] = 'http://proxy.prodemge.gov.br:8080'
  
  # Configurar genai
  genai.configure(api_key=GOOGLE_API_KEY)
  
  model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
  
  
  prompt_aux = """
  Baseado no texto a seguir, crie um texto de ofício de resposta seguindo a seguinte estrutura: Deve ser retornado apenas um texto em formato de lista, conforme o exemplo: '[<resposta>, <resposta>, <resposta>]', Sendo que cada espaço representado como resposta será o respectivo paragrafo de resposta. A seguir um exemplo de oficio utilizado por mim: ['Em atenção ao Despacho de Vossa Senhoria referente ao Ofício nº 43/SEI (106782192), que trata da proposta de alteração do art. 13 da Resolução nº 837/19, com o objetivo de restringir o acesso ao Boletim Interno Reservado (BIR) exclusivamente às Unidades ou Setores com atribuição funcional específica, informo que, conforme levantamento técnico realizado junto à PRODEMGE, o sistema SIGP WEB possui viabilidade técnica para segmentação apenas por COB (Comando Operacional de Bombeiros), embora tal funcionalidade não esteja implementada.','Destaca-se que atualmente o acesso ao BIR já é condicionado à habilitação de um perfil específico de consulta, distinto daquele utilizado para o acesso ao Boletim Interno (BI). Assim, para que um militar possa consultar os BIRs, é necessário que esteja autorizado com o respectivo perfil de acesso. A eventual segmentação por COB, caso venha a ser desenvolvida, permitirá um filtro adicional com base na vinculação do militar ao Comando correspondente, aprimorando a salvaguarda das informações restritas neste nível de articulação.','Contudo, ressalte-se que a eventual retomada de publicações e consultas descentralizadas por COB exigiria a completa desestruturação do modelo atual, com a criação de BIRs individualizados. Tal medida implicaria significativo retrabalho e aumento da complexidade de manutenção, contrariando o esforço institucional empreendido pela Ajudância-Geral na consolidação de um boletim unificado para toda a Corporação.','Diante desse cenário, e considerando a relação entre custo, benefício e a finalidade do pleito, a Subdiretoria de Tecnologia e Sistemas manifesta-se no sentido de que a modificação de sistema proposta não seja implementada. Isso porque o controle de acesso por meio de perfil específico de consulta, aliado à designação criteriosa dos operadores de BIR pelos respectivos comandantes, já poderia constituir barreira adequada à salvaguarda de informações sigilosas.','Ademais, o atual modelo não inviabiliza o acesso eventual a conteúdos de outras unidades, especialmente quando houver demanda funcional legítima, como nas atividades de inteligência. Assim, submete-se à apreciação do EMBM a real necessidade de adoção da segmentação por COB como diretriz futura para proteção do conteúdo restrito dos BIRs no SIGP WEB, considerando-se os limites técnicos e operacionais atualmente existentes. Enfatiza-se, por oportuno, que não há viabilidade técnica, no momento, para segmentações mais granulares em nível de unidade ou seção.','Permanecemos à disposição para quaisquer esclarecimentos adicionais que se fizerem necessários.']. Não se esqueça de retornar apenas a lista em texto, pois irei convertê-la para uma lista de python posteriormente. Segue o texto a ser analisado para a produção do oficio:
"""
  prompt = prompt_aux + prompt + prompt_master
  response = model.generate_content(prompt)
  
  try:
    # Tentar converter a string para lista usando eval
    response = eval(response.text)
  except:
    # Se falhar, tentar usando ast.literal_eval que é mais seguro
    import ast
    try:
      response = ast.literal_eval(response.text)
    except:
      # Se ainda falhar, fazer parsing manual
      response_text = response.text.strip()
      # Remover os colchetes externos se existirem
      if response_text.startswith('[') and response_text.endswith(']'):
        response_text = response_text[1:-1]
      # Dividir por vírgula e limpar
      response = [item.strip().strip("'\"") for item in response_text.split("',")]
  
  print('saiu make_response')
  print(response)
  return response

if __name__ == "__main__":
  prompt = "Prezado Senhor, Venho por meio deste solicitar, em nome deste batalhão, a disponibilização de computadores para uso administrativo e operacional. Ressaltamos que a aquisição desses equipamentos é fundamental para aprimorar a eficiência dos trabalhos, garantir a segurança das informações e atender às demandas crescentes das atividades militares. Solicitamos, portanto, a gentileza de informar sobre a possibilidade de atendimento a esta solicitação, bem como os procedimentos necessários para viabilizar o fornecimento dos computadores. Certos de sua atenção e colaboração, agradecemos antecipadamente. Respeitosamente Hernane Marcos de Faria Júnior SD BM SECOM do 9ºBBM"
  resposta = make_response(prompt)
  print(resposta)