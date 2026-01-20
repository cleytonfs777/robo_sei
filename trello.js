// ============================================
// Trello Module - JavaScript
// ============================================

// Estado dos labels (armazenados no localStorage)
let trelloLabels = JSON.parse(localStorage.getItem('trelloLabels') || '[]');

// Elementos do DOM
const trelloForm = document.getElementById('trelloForm');
const submitTrelloBtn = document.getElementById('submitTrelloBtn');
const clearTrelloBtn = document.getElementById('clearTrelloBtn');
const autoTitleCheckbox = document.getElementById('auto_title');
const cardTitleInput = document.getElementById('card_title');
const btnManageLabels = document.getElementById('btnManageLabels');
const labelModal = document.getElementById('labelModal');
const closeLabelModal = document.getElementById('closeLabelModal');
const addLabelBtn = document.getElementById('addLabelBtn');
const labelsList = document.getElementById('labelsList');
const labelSelect = document.getElementById('label_select');
const newLabelName = document.getElementById('new_label_name');
const newLabelColor = document.getElementById('new_label_color');

// Status elements
const trelloStatusContainer = document.getElementById('trelloStatusContainer');
const trelloStatusLog = document.getElementById('trelloStatusLog');
const closeTrelloStatus = document.getElementById('closeTrelloStatus');
const trelloProgressFill = document.getElementById('trelloProgressFill');
const trelloProgressText = document.getElementById('trelloProgressText');

// ============================================
// Labels Management
// ============================================

function renderLabels() {
    // Atualizar lista no modal
    labelsList.innerHTML = '';
    
    if (trelloLabels.length === 0) {
        labelsList.innerHTML = '<p style="color: #999; text-align: center; padding: 2rem;">Nenhum label cadastrado</p>';
    } else {
        trelloLabels.forEach((label, index) => {
            const labelItem = document.createElement('div');
            labelItem.className = 'label-item';
            labelItem.style.borderLeftColor = getLabelColorHex(label.color);
            
            labelItem.innerHTML = `
                <div class="label-item-info">
                    <div class="label-color-box color-${label.color}"></div>
                    <span class="label-item-name">${label.name}</span>
                    <span class="label-item-color">(${getLabelColorName(label.color)})</span>
                </div>
                <div class="label-item-actions">
                    <button class="btn-icon-only delete" onclick="deleteLabel(${index})" title="Excluir">
                        🗑️
                    </button>
                </div>
            `;
            
            labelsList.appendChild(labelItem);
        });
    }
    
    // Atualizar select de labels
    labelSelect.innerHTML = '<option value="">Selecione um label...</option>';
    trelloLabels.forEach((label, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${label.name} (${getLabelColorName(label.color)})`;
        labelSelect.appendChild(option);
    });
}

function getLabelColorHex(colorName) {
    const colors = {
        red: '#eb5a46',
        orange: '#ff9f1a',
        yellow: '#f2d600',
        green: '#61bd4f',
        blue: '#0079bf',
        purple: '#c377e0',
        pink: '#ff78cb',
        sky: '#00c2e0',
        lime: '#51e898',
        black: '#344563'
    };
    return colors[colorName] || '#999';
}

function getLabelColorName(colorName) {
    const colorNames = {
        red: 'Vermelho',
        orange: 'Laranja',
        yellow: 'Amarelo',
        green: 'Verde',
        blue: 'Azul',
        purple: 'Roxo',
        pink: 'Rosa',
        sky: 'Azul Claro',
        lime: 'Verde Limão',
        black: 'Preto'
    };
    return colorNames[colorName] || colorName;
}

function addLabel() {
    const name = newLabelName.value.trim();
    const color = newLabelColor.value;
    
    if (!name) {
        alert('Por favor, digite um nome para o label');
        return;
    }
    
    trelloLabels.push({ name, color });
    localStorage.setItem('trelloLabels', JSON.stringify(trelloLabels));
    
    newLabelName.value = '';
    newLabelColor.value = 'red';
    
    renderLabels();
}

function deleteLabel(index) {
    if (confirm('Tem certeza que deseja excluir este label?')) {
        trelloLabels.splice(index, 1);
        localStorage.setItem('trelloLabels', JSON.stringify(trelloLabels));
        renderLabels();
    }
}

// ============================================
// Modal Management
// ============================================

function openModal() {
    labelModal.classList.add('show');
}

function closeModal() {
    labelModal.classList.remove('show');
}

// ============================================
// Title Generation
// ============================================

autoTitleCheckbox.addEventListener('change', function() {
    if (this.checked) {
        cardTitleInput.disabled = true;
        cardTitleInput.placeholder = 'Será gerado automaticamente pela IA...';
    } else {
        cardTitleInput.disabled = false;
        cardTitleInput.placeholder = 'Ex: Sistema de Controle de Protocolos';
    }
});

// ============================================
// Status Management
// ============================================

function addTrelloStatus(message, type = 'info', progress = null) {
    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };

    const statusItem = document.createElement('div');
    statusItem.className = `status-item status-${type}`;
    statusItem.innerHTML = `
        <span class="status-icon">${icons[type]}</span>
        <span class="status-message">${message}</span>
        <span class="status-time">${new Date().toLocaleTimeString()}</span>
    `;
    
    trelloStatusLog.appendChild(statusItem);
    trelloStatusLog.scrollTop = trelloStatusLog.scrollHeight;

    if (progress !== null) {
        updateTrelloProgress(progress);
    }
}

function updateTrelloProgress(percentage) {
    trelloProgressFill.style.width = `${percentage}%`;
    trelloProgressText.textContent = `${percentage}%`;
}

function showTrelloStatus() {
    trelloStatusContainer.classList.remove('hidden');
    trelloStatusLog.innerHTML = '';
    updateTrelloProgress(0);
}

function hideTrelloStatus() {
    trelloStatusContainer.classList.add('hidden');
}

// ============================================
// Form Submission
// ============================================

trelloForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const boardName = document.getElementById('board_name').value;
    const labelIndex = document.getElementById('label_select').value;
    const autoTitle = document.getElementById('auto_title').checked;
    let cardTitle = document.getElementById('card_title').value;
    const cardDescription = document.getElementById('card_description').value;
    const listName = document.getElementById('list_name').value;
    const dueDate = document.getElementById('due_date').value;
    
    // Validações
    if (!labelIndex) {
        alert('Por favor, selecione um label');
        return;
    }
    
    if (!autoTitle && !cardTitle) {
        alert('Por favor, preencha o título ou marque para gerar automaticamente');
        return;
    }
    
    showTrelloStatus();
    submitTrelloBtn.disabled = true;
    submitTrelloBtn.classList.add('loading');
    
    try {
        const selectedLabel = trelloLabels[labelIndex];
        
        addTrelloStatus('Iniciando criação do card no Trello...', 'info', 10);
        
        // Preparar dados
        const formData = {
            board_name: boardName,
            label_name: selectedLabel.name,
            label_color: selectedLabel.color,
            auto_title: autoTitle,
            card_title: cardTitle,
            card_description: cardDescription,
            list_name: listName,
            due_date: dueDate || null,
            use_ai: true  // Sempre usar IA para formatar
        };

        console.log(`Board: ${boardName}, Label: ${selectedLabel.name} (${selectedLabel.color}), Auto Title: ${autoTitle}, Title: ${cardTitle}, Description Length: ${cardDescription.length}, List: ${listName}, Due Date: ${dueDate}`);
        
        addTrelloStatus('Formatando descrição com IA...', 'info', 30);
        
        // Enviar para o backend
        const response = await fetch('/criar-card-trello', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            addTrelloStatus('Card criado com sucesso!', 'success', 100);
            
            if (result.card_url) {
                addTrelloStatus(`Acessar card: ${result.card_url}`, 'info');
            }
            
            // Limpar formulário após sucesso
            setTimeout(() => {
                trelloForm.reset();
                cardTitleInput.disabled = false;
                cardTitleInput.placeholder = 'Ex: Sistema de Controle de Protocolos';
            }, 2000);
        } else {
            addTrelloStatus(result.error || 'Erro ao criar card', 'error', 100);
        }
        
    } catch (error) {
        console.error('Erro:', error);
        addTrelloStatus('Erro ao processar requisição: ' + error.message, 'error', 100);
    } finally {
        submitTrelloBtn.disabled = false;
        submitTrelloBtn.classList.remove('loading');
    }
});

// ============================================
// Clear Form
// ============================================

clearTrelloBtn.addEventListener('click', function() {
    if (confirm('Tem certeza que deseja limpar o formulário?')) {
        trelloForm.reset();
        cardTitleInput.disabled = false;
        cardTitleInput.placeholder = 'Ex: Sistema de Controle de Protocolos';
    }
});

// ============================================
// Event Listeners
// ============================================

btnManageLabels.addEventListener('click', openModal);
closeLabelModal.addEventListener('click', closeModal);
addLabelBtn.addEventListener('click', addLabel);
closeTrelloStatus.addEventListener('click', hideTrelloStatus);

// Fechar modal ao clicar fora
labelModal.addEventListener('click', function(e) {
    if (e.target === labelModal) {
        closeModal();
    }
});

// Adicionar label com Enter
newLabelName.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        addLabel();
    }
});

// ============================================
// Initialization
// ============================================

// Inicializar labels ao carregar
renderLabels();

// Adicionar alguns labels padrão se não existir nenhum
if (trelloLabels.length === 0) {
    trelloLabels = [
        { name: 'Urgente', color: 'red' },
        { name: 'Em Andamento', color: 'yellow' },
        { name: 'Concluído', color: 'green' },
        { name: 'Bug', color: 'orange' },
        { name: 'Feature', color: 'blue' }
    ];
    localStorage.setItem('trelloLabels', JSON.stringify(trelloLabels));
    renderLabels();
}
