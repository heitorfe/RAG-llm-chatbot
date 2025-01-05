Segue o **README.md** com instruções detalhadas e melhorias para o arquivo `.env`:

---

# Deploy da Infraestrutura com Bicep e Configuração Python

Este repositório contém os arquivos necessários para configurar e implementar uma infraestrutura na Azure com Bicep. Siga os passos abaixo para realizar o deploy e configurar os serviços necessários.

## Pré-requisitos

1. **Ferramentas instaladas**:
   * [Azure CLI](https://learn.microsoft.com/pt-br/cli/azure/install-azure-cli)
   * [Visual Studio Code](https://code.visualstudio.com/) com a extensão Bicep
   * [Python 3.9+](https://www.python.org/downloads/)
   * [Git](https://git-scm.com/)

2. **Permissões necessárias**:
   * Acesso à sua conta Azure com permissões para criar e gerenciar recursos.
   * Permissões para atribuição de papéis (`roleAssignments`).

---

## Passo a Passo

### 1. Configurar o ambiente

Certifique-se de que você está conectado à sua conta Azure:
```bash
az login
```

Se necessário, defina o escopo para o grupo de recursos:
```bash
az group create --name NomeDoResourceGroup --location Localizacao
```

### 2. Executar o script principal do Bicep

Execute o arquivo `main.bicep` para provisionar os recursos na Azure:
```bash
az deployment group create --resource-group NomeDoResourceGroup --template-file main.bicep --parameters env=<nome-do-ambiente>
```
Substitua `<nome-do-ambiente>` por valores como `dev`, `test` ou `prod`.

* Quando o script terminar de executar, cria o segredo no Azure Key Vault: `atlassian-token` com a chave de API da Atlassian.
---

### 3. Configurar variáveis de ambiente

Preencha o arquivo `.env` com as informações geradas pelo deploy. Use o modelo abaixo como referência:

```env
# Serviço de Busca do Azure
AZURE_SEARCH_SERVICE=<NOME_DO_SERVICO_DE_BUSCA>
AZURE_SEARCH_KEY=<CHAVE_DE_ACESSO>

# Serviço OpenAI do Azure
AZURE_OPENAI_ACCOUNT=<NOME_DA_CONTA_OPENAI>
AZURE_OPENAI_KEY=<CHAVE_DE_ACESSO_OPENAI>


# Conta de Armazenamento do Azure
AZURE_STORAGE_CONNECTION=<STRING_DE_CONEXAO_STORAGE>
```

#### Dicas para Preencher o `.env`:
- Use o portal da Azure para localizar os nomes dos serviços e as chaves de acesso.
- Certifique-se de que todas as chaves estão atualizadas e corretas.

---

### 4. Configurar a aplicação Python

Com o ambiente configurado, execute os comandos de configuração para inicializar os serviços:
```bash
python -m venv .venv
.venv/scripts/activate
pip install -r requirements.txt
python config/search_config.py
```

Este script irá:
* Criar uma virtual enviroment e ativar
* Instalar dependências
* Configurar parâmetros específicos no serviço de busca.
* Validar a conexão com os serviços configurados.

#### Depois ative a deleção incremental nativa nas fontes de dados. Não é possível fazer essa configuração via código.
---

## Estrutura do Projeto

```
/
├── main.bicep                # Script principal de deploy
├── modules/                  # Módulos individuais de Bicep
│   ├── storage.bicep         # Configuração da Conta de Armazenamento
│   ├── function.bicep        # Configuração do Function App
│   ├── search.bicep          # Configuração do Serviço de Busca
│   ├── openai.bicep          # Configuração do Serviço OpenAI
├── config/
│   └── search_config.py      # Script Python para configurar o serviço de busca
└── .env.example              # Exemplo do arquivo de variáveis de ambiente
```

---

## Solução de Problemas

- **Erro ao criar recursos no Azure**:
  * Verifique se as permissões de conta estão corretas.
  * Confirme se o Azure CLI está atualizado.

- **Problemas com o arquivo `.env`**:
  * Certifique-se de que os valores foram preenchidos corretamente.
  * Valide as chaves de acesso no portal da Azure.

---

## Contato

Caso encontre problemas ou precise de suporte, entre em contato com o administrador do projeto.

--- 

O arquivo `.env` foi melhorado para incluir descrições de variáveis mais específicas, e o README fornece instruções detalhadas e práticas.