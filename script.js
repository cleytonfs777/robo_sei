// Elementos do DOM
const form = document.getElementById('oficioForm');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const statusContainer = document.getElementById('statusContainer');
const statusLog = document.getElementById('statusLog');
const closeStatusBtn = document.getElementById('closeStatus');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const msgTextarea = document.getElementById('msg');
const charCounter = document.getElementById('charCounter');

// Elementos do gerador de despacho
const btnGerarMsg = document.getElementById('btnGerarMsg');
const despachoGenerator = document.getElementById('despachoGenerator');
const btnAddDoc = document.getElementById('btnAddDoc');
const btnGerarTexto = document.getElementById('btnGerarTexto');
const nomeDocumentoInput = document.getElementById('nomeDocumento');
const artigoSelect = document.getElementById('artigo');
const listaDocumentos = document.getElementById('listaDocumentos');
const atribuicaoSelect = document.getElementById('atribuicao');
const assuntoInput = document.getElementById('assunto');
const complementoInput = document.getElementById('complemento');
const alertDespacho = document.getElementById('alertDespacho');

let documentos = [];

// Lista de atribuições (mesmo do atribuidor.html)
const listaAtribuicoes = [
    "Ten Paiva",
    "Maj Vicente",
    "Maj Couto",
    "Maj Giovanny",
    "Maj Rocha",
    "Cap Linke",
    "Cap Alexandre",
    "Sgt Damásio",
    "Sgt Sandro",
    "Ten Cesar Alves",
    "Cel Stella",
    "Ten Cel Montezano"
];

// Ícones para diferentes tipos de status
const statusIcons = {
    info: 'ℹ️',
    success: '✅',
    error: '❌',
    warning: '⚠️'
};

// Função para atualizar o contador de caracteres
function updateCharCounter() {
    const length = msgTextarea.value.length;
    charCounter.textContent = `${length}/250 caracteres`;
    
    // Remover classes anteriores
    charCounter.classList.remove('warning', 'error');
    
    // Adicionar classe baseada no comprimento
    if (length > 250) {
        charCounter.classList.add('error');
    } else if (length > 200) {
        charCounter.classList.add('warning');
    }
}

// Event listener para o textarea
if (msgTextarea) {
    msgTextarea.addEventListener('input', updateCharCounter);
}

// ============= GERADOR DE DESPACHO =============

// Função para mostrar/ocultar o gerador de despacho
function toggleDespachoGenerator() {
    despachoGenerator.classList.toggle('hidden');
    if (alertDespacho) {
        alertDespacho.classList.add('hidden');
    }
}

// Função para adicionar documento
function adicionarDocumento() {
    const artigo = artigoSelect.value;
    const nomeDoc = nomeDocumentoInput.value.trim();

    if (!nomeDoc) {
        alert('Digite o nome do documento');
        return;
    }

    const documento = `${artigo} ${nomeDoc}`;
    documentos.push(documento);
    atualizarListaDocumentos();

    // Limpar campo
    nomeDocumentoInput.value = '';
}

// Função para atualizar a lista de documentos
function atualizarListaDocumentos() {
    listaDocumentos.innerHTML = '';

    if (documentos.length === 0) {
        listaDocumentos.innerHTML = '<p style="text-align: center; color: #64748b; padding: 1rem;">Nenhum documento adicionado</p>';
        return;
    }

    documentos.forEach((doc, index) => {
        const div = document.createElement('div');
        div.className = 'doc-item';
        div.innerHTML = `
            <span>${doc}</span>
            <button type="button" class="btn-remove-doc" onclick="removerDocumento(${index})">Remover</button>
        `;
        listaDocumentos.appendChild(div);
    });
}

// Função para remover documento
function removerDocumento(index) {
    documentos.splice(index, 1);
    atualizarListaDocumentos();
}

// Função para formatar lista de itens
function formatarItens(lista) {
    if (lista.length === 1) {
        return lista[0];
    } else if (lista.length === 2) {
        return `${lista[0]} e ${lista[1]}`;
    } else {
        return lista.slice(0, -1).join(', ') + ' e ' + lista[lista.length - 1];
    }
}

// Função para obter tratamento inicial
function getTratamentoInicial(nome) {
    if (nome === "Cel Stella") {
        return "Sra.";
    } else if (nome.startsWith("Maj ") || nome.startsWith("Ten Cel ") || nome.startsWith("Cel ")) {
        return "Sr.";
    } else {
        return "";
    }
}

// Função para obter despedida
function getDespedida(nome) {
    if (nome.startsWith("Maj ") || nome.startsWith("Ten Cel ") || nome.startsWith("Cel ")) {
        return "Resp,";
    } else if (nome.startsWith("Sd ") || nome.startsWith("Cb ") || nome.startsWith("Sgt ") || nome.startsWith("Ten ")) {
        return "Att,";
    } else {
        return "Cord,";
    }
}

// Função para gerar o texto do despacho
function gerarTextoDespacho() {
    const atribuicao = atribuicaoSelect.value;
    const assunto = assuntoInput.value.trim();
    const complemento = complementoInput.value.trim();

    // Ocultar alerta anterior
    if (alertDespacho) {
        alertDespacho.classList.add('hidden');
    }

    if (!atribuicao || !assunto) {
        if (alertDespacho) {
            alertDespacho.textContent = '⚠️ Preencha os campos: Atribuição e Assunto';
            alertDespacho.className = 'alert-despacho warning';
            alertDespacho.classList.remove('hidden');
        } else {
            alert('Preencha os campos: Atribuição e Assunto');
        }
        return;
    }

    if (documentos.length === 0) {
        if (alertDespacho) {
            alertDespacho.textContent = '⚠️ Adicione pelo menos um documento';
            alertDespacho.className = 'alert-despacho warning';
            alertDespacho.classList.remove('hidden');
        } else {
            alert('Adicione pelo menos um documento');
        }
        return;
    }

    const tratamentoInicial = getTratamentoInicial(atribuicao);
    const stringOficios = formatarItens(documentos);
    const complementoTexto = complemento ? `${complemento}. ` : '';
    const tratamento = documentos.length === 1 ? 'trata' : 'tratam';
    const despedida = getDespedida(atribuicao);

    // Montar o texto inicial - sempre inclui o nome, com ou sem Sr./Sra.
    const inicioTexto = tratamentoInicial ? `${tratamentoInicial} ${atribuicao}. ` : `${atribuicao}. `;
    
    // Definir o texto de encaminhamento baseado no tratamento
    const textoEncaminhamento = tratamentoInicial ? 'Encaminho a V.Sa. para analise e despacho' : 'Encaminho para analise e despacho';

    const textoFinal = `${inicioTexto}${textoEncaminhamento} ${stringOficios}, que ${tratamento} de ${assunto}. ${complementoTexto}${despedida} Cap Cleyton.`;

    // Inserir no textarea
    msgTextarea.value = textoFinal;
    updateCharCounter();

    // Verificar se excede 250 caracteres
    if (textoFinal.length > 250) {
        if (alertDespacho) {
            alertDespacho.innerHTML = `❌ <strong>ERRO:</strong> Texto com ${textoFinal.length} caracteres (limite: 250)!<br><small>Reduza o complemento, nomes dos documentos ou assunto.</small>`;
            alertDespacho.className = 'alert-despacho error';
            alertDespacho.classList.remove('hidden');
        } else {
            alert(`⚠️ ATENÇÃO: O texto gerado tem ${textoFinal.length} caracteres, excedendo o limite de 250!\n\nConsidere:\n- Reduzir o complemento\n- Simplificar nomes dos documentos\n- Reduzir o assunto`);
        }
    } else {
        if (alertDespacho) {
            alertDespacho.innerHTML = `✅ <strong>Texto Válido!</strong> ${textoFinal.length}/250 caracteres`;
            alertDespacho.className = 'alert-despacho success';
            alertDespacho.classList.remove('hidden');
        }
        
        // Ocultar o gerador após 2 segundos se o texto for válido
        setTimeout(() => {
            despachoGenerator.classList.add('hidden');
        }, 2000);
    }
}

// Event Listeners do gerador de despacho
if (btnGerarMsg) {
    btnGerarMsg.addEventListener('click', toggleDespachoGenerator);
}

if (btnAddDoc) {
    btnAddDoc.addEventListener('click', adicionarDocumento);
}

if (btnGerarTexto) {
    btnGerarTexto.addEventListener('click', gerarTextoDespacho);
}

if (nomeDocumentoInput) {
    nomeDocumentoInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            adicionarDocumento();
        }
    });
}

// ============= FIM DO GERADOR DE DESPACHO =============

// Função para adicionar mensagem de status
function addStatusMessage(tipo, mensagem, progresso = null) {
    const statusItem = document.createElement('div');
    statusItem.className = `status-item ${tipo}`;
    
    const icon = document.createElement('span');
    icon.className = 'status-icon';
    icon.textContent = statusIcons[tipo] || 'ℹ️';
    
    const message = document.createElement('span');
    message.className = 'status-message';
    
    // Adicionar percentual se fornecido
    if (progresso !== null && progresso !== undefined) {
        message.innerHTML = `<strong>[${progresso}%]</strong> ${mensagem}`;
    } else {
        message.textContent = mensagem;
    }
    
    statusItem.appendChild(icon);
    statusItem.appendChild(message);
    statusLog.appendChild(statusItem);
    
    // Auto-scroll para a última mensagem
    statusLog.scrollTop = statusLog.scrollHeight;
    
    // Atualizar barra de progresso se fornecido
    if (progresso !== null && progresso !== undefined) {
        updateProgress(progresso);
    }
}

// Função para limpar o log de status
function clearStatusLog() {
    statusLog.innerHTML = '';
    progressFill.style.width = '0%';
    progressText.textContent = '0%';
}

// Função para atualizar a barra de progresso
function updateProgress(percentage) {
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
    
    // Mostrar texto apenas quando houver espaço suficiente (>10%)
    if (percentage >= 10) {
        progressText.style.opacity = '1';
    } else {
        progressText.style.opacity = '0';
    }
}

// Função para processar o formulário
async function handleSubmit(e) {
    e.preventDefault();
    
    // Desabilitar botão de submit
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Processando...';
    
    // Mostrar container de status
    statusContainer.classList.remove('hidden');
    clearStatusLog();
    
    // Coletar dados do formulário
    const signatarioSelect = document.getElementById('signatario');
    
    // Validar se um signatário foi selecionado
    if (!signatarioSelect.value || signatarioSelect.value === "") {
        addStatusMessage('error', 'Por favor, selecione um signatário!');
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<span class="btn-icon">🚀</span> Criar Ofício';
        return;
    }
    
    const formData = {
        doc_sei: document.getElementById('doc_sei').value,
        processo: document.getElementById('processo').value,
        assunto: document.getElementById('assunto').value,
        destinatario: document.getElementById('destinatario').value,
        signatario: signatarioSelect.options[signatarioSelect.selectedIndex].text,
        graduacao: document.getElementById('graduacao').value,
        funcao: document.getElementById('funcao').value,
        etiqueta: document.getElementById('etiqueta').value,
        atribuicao: document.getElementById('atribuicao').value,
        msg: document.getElementById('msg').value,
        ofreferencia: document.getElementById('ofreferencia').value,
        complementar: document.getElementById('complementar').value || "",
        has_ticket: document.getElementById('has_ticket').value === "sim"
    };
    
    // Validar tamanho da mensagem
    if (formData.msg.length > 250) {
        addStatusMessage('error', 'A mensagem da anotação não pode ter mais de 250 caracteres!');
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<span class="btn-icon">🚀</span> Criar Ofício';
        return;
    }
    
    try {
        addStatusMessage('info', 'Iniciando requisição ao servidor...');
        updateProgress(10);
        
        // Fazer requisição para a API
        const response = await fetch('http://localhost:8000/responde_processo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        // Ler o stream de resposta
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                break;
            }
            
            // Decodificar o chunk
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    addStatusMessage(data.tipo, data.mensagem, data.progresso);
                } catch (e) {
                    console.error('Erro ao parsear JSON:', e);
                }
            }
        }
        
        addStatusMessage('success', 'Processo concluído com sucesso!');
        
    } catch (error) {
        addStatusMessage('error', `Erro ao processar: ${error.message}`);
        console.error('Erro:', error);
    } finally {
        // Reabilitar botão de submit
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<span class="btn-icon">🚀</span> Criar Ofício';
    }
}

// Função para limpar o formulário
function handleClear() {
    form.reset();
    statusContainer.classList.add('hidden');
    clearStatusLog();
    documentos = [];
    atualizarListaDocumentos();
    updateCharCounter();
    despachoGenerator.classList.add('hidden');
    if (complementoInput) complementoInput.value = '';
    if (nomeDocumentoInput) nomeDocumentoInput.value = '';
}

// Função para fechar o status
function handleCloseStatus() {
    statusContainer.classList.add('hidden');
}

// Event Listeners
form.addEventListener('submit', handleSubmit);
clearBtn.addEventListener('click', handleClear);
closeStatusBtn.addEventListener('click', handleCloseStatus);

// Preencher valores padrão para teste (opcional - remova em produção)
document.addEventListener('DOMContentLoaded', () => {
    // Valores de exemplo (comente ou remova estas linhas se não quiser valores padrão)
    /*
    document.getElementById('doc_sei').value = '126086248';
    document.getElementById('processo').value = '1400.01.0074829/2025-05';
    document.getElementById('assunto').value = 'Resposta quanto a esclarecimentos adicionais sobre o Contrato Álea (CBMMG x UFJF)';
    document.getElementById('destinatario').value = 'Senhor Ten Cel BM, Resp p/ pelo 5ºCOB';
    document.getElementById('signatario').value = 'Stella Coeli Flori Maciel';
    document.getElementById('graduacao').value = 'Cel BM';
    document.getElementById('funcao').value = 'Diretora de Logística e Finanças';
    */
});
