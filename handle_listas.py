# Faz a leitura do json dadosmil.json e armazena em um dicionário
# em uma lista chamada dados

import json


def lista_all_names():
    lista_nomes = []

    with open('dadosmil.json', encoding='utf-8') as json_file:
        dados = json.load(json_file)

        for item in dados.values():

            lista_nomes.append(item[1])

    # Ordenar a lista em ordem crescente
    lista_nomes.sort()

    return lista_nomes


def data_militar(militar):
    with open('dadosmil.json', encoding='utf-8') as json_file:
        dados = json.load(json_file)

        for valor in dados.values():
            if valor[1] == militar:
                return valor


def status():
    return [
        "Concluído",
        "Em andamento (SDTS/NTS)",
        "Em andamento (Outros)",
    ]


def categoria():
    return [
        "Telefonia",
        "Rádio",
        "DSP",
        "Processo de compra",
        "Convênio",
        "SMP",
        "Outros",
    ]


def atendente():
    return [
        "Cap Cleyton",
        "Sgt Leonardo",
        "Sd Zenatelli",
    ]


def etiqueta():
    return [
        "Aguardando Despacho Diretor",
        "Aguardando Despacho do Major",
        "Aguardando Despacho do SDTS",
        "Compartilhamentos de site aguardando projeto",
        "Compartilhamentos de site deferidos",
        "Compartilhamentos de site em análise PM",
        "Divulgação Geral",
        "NTS",
        "NTS - Contratos",
        "NTS - DSP's 2023",
        "NTS - DSP's 2024",
        "NTS - Seção de Informática",
        "NTS - Seção de Sistemas",
        "NTS - Seção de Telecomunicações",
        "Patrimônio NTS",
        "Postes de Telecom CBMMG",
        "Prioridade - Urgente",
        "SDTS1 - Seção de Informática",
        "Seção de Sistemas",
        "Seção de Telecomunicações",
        "não utilzado"
    ]


def tranform_text_atribuicao(text):
    # Retirar espaços em text
    text = text.strip()
    with open('dadosmil.json', encoding='utf-8') as json_file:
        dados = json.load(json_file)

        for chave, valor in dados.items():
            if valor[1] == text:
                print(f"Dado para atribuição: {chave} - {valor[0]}")
                return f"{chave} - {valor[0]}"
