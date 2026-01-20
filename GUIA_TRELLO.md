# 📋 Guia de Uso - Gerador de Trello

## Visão Geral

O Gerador de Trello é um módulo do SDTS-3 Tools que automatiza a criação de cards no Trello com formatação profissional via IA, seguindo os padrões de um Product Owner e Arquiteto de Software.

## 🎯 Funcionalidades

### 1. Gerenciamento de Labels
- Cadastro de labels personalizados
- 10 cores disponíveis
- Edição e exclusão de labels
- Armazenamento local no navegador

### 2. Geração Automática com IA
- **Título Automático**: A IA analisa a descrição e gera um título adequado
- **Formatação da Descrição**: Transforma texto simples em card estruturado completo

### 3. Estrutura do Card Gerado

Cada card criado inclui automaticamente:

- 🧩 **Visão Geral** - Propósito e contexto do projeto
- 🎯 **Objetivos e Resultados Esperados** - Metas mensuráveis
- 👥 **Perfis de Usuário e Permissões** - RBAC e auditoria
- 📦 **Escopo Funcional (MVP)** - Funcionalidades mínimas
- 🧱 **Requisitos Não Funcionais** - Segurança, performance, disponibilidade
- 🛠️ **Arquitetura Proposta** - Componentes e padrões
- 🗃️ **Modelo de Dados** - Entidades e relacionamentos
- 🔌 **Integrações e Dependências** - Sistemas externos
- 🔒 **Segurança e Conformidade** - Controles e proteções
- ✅ **Critérios de Aceite** - Verificações objetivas
- 🧪 **Plano de Testes** - Estratégia de testes
- 🚀 **Próximos Passos** - Backlog priorizado

## 📝 Como Usar

### Passo 1: Acessar o Módulo

1. Abra o SDTS-3 Tools em `http://localhost:8000`
2. Clique em "Gerador de Trello" no menu lateral

### Passo 2: Configurar Labels (Primeira vez)

1. Clique em "⚙️ Gerenciar" ao lado do campo Label
2. Adicione seus labels personalizados:
   - Digite o nome (ex: "Urgente", "Bug", "Feature")
   - Escolha uma cor
   - Clique em "➕ Adicionar Label"
3. Os labels são salvos automaticamente no navegador

**Labels Padrão Incluídos:**
- 🔴 Urgente (Vermelho)
- 🟡 Em Andamento (Amarelo)
- 🟢 Concluído (Verde)
- 🟠 Bug (Laranja)
- 🔵 Feature (Azul)

### Passo 3: Preencher o Formulário

#### Campos Obrigatórios:

1. **Nome do Board** 
   - Exemplo: `SDTS-3 - Projetos 2025`
   
2. **Label**
   - Selecione um label da lista configurada
   
3. **Título do Card**
   - Digite manualmente OU
   - Marque "Gerar automaticamente com IA" para a IA criar o título
   
4. **Descrição**
   - Descreva o projeto de forma livre
   - Quanto mais detalhes, melhor o resultado
   - A IA irá estruturar e expandir automaticamente
   
5. **Nome da Lista**
   - Exemplo: `Backlog`, `Em Desenvolvimento`, `Concluído`

#### Campos Opcionais:

6. **Data de Vencimento**
   - Selecione uma data se o card tiver prazo

### Passo 4: Criar o Card

1. Clique em "🚀 Criar Card no Trello"
2. Acompanhe o progresso:
   - Formatação da descrição pela IA
   - Criação do card no Trello
   - Status final com link do card

## 💡 Dicas de Uso

### Para Melhores Resultados na Descrição:

**✅ BOM:**
```
Sistema para controlar protocolos do CBMMG. 
Precisa ter cadastro de documentos, busca avançada, 
relatórios, integração com SEI e controle de permissões 
por unidade.
```

**❌ EVITE:**
```
Fazer um sistema
```

### Exemplos de Descrições:

#### Exemplo 1 - Sistema Simples:
```
Criar um sistema de controle de escalas de serviço para o quartel. 
Deve permitir cadastrar militares, definir escalas mensais, 
enviar notificações automáticas e gerar relatórios de horas trabalhadas.
```

#### Exemplo 2 - Integração:
```
Desenvolver uma integração entre o sistema de protocolos e o Trello. 
Quando um novo processo urgente for criado no SEI, deve criar 
automaticamente um card no Trello com os dados do processo.
```

#### Exemplo 3 - Dashboard:
```
Dashboard gerencial para acompanhamento de projetos do SDTS-3. 
Visualizar status de todos os projetos, gráficos de progresso, 
alertas de prazos vencendo, integração com Trello e GitHub.
```

## 🔧 Configuração Avançada

### Cores de Labels Disponíveis:

| Emoji | Cor | Código Trello |
|-------|-----|---------------|
| 🔴 | Vermelho | `red` |
| 🟠 | Laranja | `orange` |
| 🟡 | Amarelo | `yellow` |
| 🟢 | Verde | `green` |
| 🔵 | Azul | `blue` |
| 🟣 | Roxo | `purple` |
| 🩷 | Rosa | `pink` |
| 🔷 | Azul Claro | `sky` |
| 🟩 | Verde Limão | `lime` |
| ⚫ | Preto | `black` |

### Gerenciamento de Labels:

- **Adicionar**: Clique em "Gerenciar" → Digite nome e cor → "Adicionar"
- **Excluir**: Clique no 🗑️ ao lado do label → Confirme
- **Backup**: Os labels ficam salvos no navegador (localStorage)

## ⚠️ Notas Importantes

1. **Internet Necessária**: A IA precisa de conexão para processar
2. **API Key**: Configure `GOOGLE_API_KEY` no arquivo `.env`
3. **Trello API**: Para integração completa, configure também:
   - `TRELLO_API_KEY`
   - `TRELLO_TOKEN`
4. **Tempo de Processamento**: A IA pode levar 5-15 segundos

## 🐛 Resolução de Problemas

### Erro: "Por favor, selecione um label"
- **Solução**: Configure pelo menos um label em "Gerenciar Labels"

### Erro: "Erro ao criar card"
- **Causa**: Problema com API Key da IA
- **Solução**: Verifique o arquivo `.env` e reinicie o servidor

### Card não aparece no Trello
- **Causa**: Integração com API do Trello não configurada
- **Solução**: Adicione as credenciais do Trello no `.env`

### Título não é gerado automaticamente
- **Causa**: Checkbox não marcado ou erro na IA
- **Solução**: Marque "Gerar automaticamente" e tente novamente

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este guia
2. Consulte o arquivo `README.md`
3. Entre em contato com o SDTS-3

---

**Versão:** 1.0.0  
**Última atualização:** Janeiro 2026
