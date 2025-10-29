from handle_listas import data_militar


def formatar_itens(lista):
    if len(lista) == 1:
        return lista[0]
    elif len(lista) == 2:
        return f"{lista[0]} e {lista[1]}"
    else:
        # Junta todos os elementos exceto o último com ", "
        # e adiciona o último elemento com " e " antes dele
        return ", ".join(lista[:-1]) + " e " + lista[-1]


def generate_text(atribuicao: str = "", assunto: str = "",  documentos: list[str] = [], complemento: str = "") -> str:
    dados_militar = data_militar(atribuicao)
    if not dados_militar:
        dados_militar = ["", "", "", "", ""]
    string_oficios = formatar_itens(documentos)
    complemento = f"{complemento}. " if complemento else ""
    tratamento = "trata" if len(documentos) == 1 else "tratam"

    frase_final = f"{dados_militar[2]} {dados_militar[1]}. {dados_militar[4]} {string_oficios}, que {tratamento} de {assunto}. {complemento}{dados_militar[3]} Cap Cleyton."

    return frase_final


if __name__ == "__main__":
    print(generate_text("Maj Giovanny",
          "Instalação de Repetidoras para funcionamento da rede radio", ["o Oficio 1"]))
