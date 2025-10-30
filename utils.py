def cria_oficio(assunto: str, destinatario: str, signatario: str, graduacao: str, funcao: str, paragrafos: list, ofreferencia: str, is_upper=True) -> str:
    
    if is_upper:
        signatario = signatario.upper()
        graduacao = graduacao.upper()
        funcao = funcao.upper()
    
    lista_principal = ''
    for i in paragrafos:
        lista_principal += f'<p class="Texto_Justificado_Recuo_Primeira_Linha">{i}</p>'
    conteudo_oficio = f"""
    <body>
        <p class="Texto_Alinhado_Esquerda"><strong>Assunto: {assunto}</strong></p>
        <p class="Texto_Alinhado_Esquerda"><strong>Referencia: {ofreferencia}</strong></p>
        <p class="Texto_Justificado_Recuo_Primeira_Linha">&nbsp;</p>
        <p class="Texto_Justificado_Recuo_Primeira_Linha"><strong>{destinatario},</strong></p>
        <p class="Texto_Justificado_Recuo_Primeira_Linha">&nbsp;</p>
        {lista_principal}
        <p class="Texto_Justificado_Recuo_Primeira_Linha">&nbsp;</p>
        <p class="Texto_Justificado_Recuo_Primeira_Linha">Respeitosamente,</p>
        <p style="margin-top:0; margin-right:0; margin-bottom:11px; margin-left:0">&nbsp;</p>
        <p class="Nome_Signatário">{signatario}, {graduacao}</p>
        <p class="Nome_Signatário">{funcao}</p>
    </body>
    """
    return conteudo_oficio

if __name__ == "__main__":
    assunto = "Solicitação de liberação de atividades de curso"
    destinatario = "Senhora Primeiro Tenente BM Chefe de Curso do CFS - Caparaó"
    signatario = "Hernane Marcos de Faria Júnior"
    graduacao = "Soldado BM"
    funcao = "Solicitante/CFS Alfa - Turma Caparaó"
    paragrafos = ["""Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.""",
                """Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.""",
                """Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.""",
                """Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."""
                ]
    oficio = cria_oficio(assunto, destinatario, signatario, graduacao, funcao, paragrafos)
    
    with open("oficio.html", "w", encoding="utf-8") as f:
        f.write(oficio)