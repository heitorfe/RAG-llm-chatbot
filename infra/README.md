# Infraestrutura do Projeto

Este projeto utiliza diversos serviços do Azure, incluindo Azure Cognitive Search, Azure OpenAI e Azure Storage. Este README fornece instruções sobre como configurar a infraestrutura e o arquivo `.env`.

## Configuração da Infraestrutura

### Pré-requisitos

- Azure CLI instalado
- Conta no Azure com permissões para criar recursos

### Passos para Configuração

1. Clone o repositório:
    ```sh
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```

2. Configure os parâmetros no arquivo `parameters.json`

3. Execute o script de implantação e siga os passos orientados no terminal:
    ```sh
    ./deploy.ps1
    ```

4. Preencha o arquivo [.env](http://_vscodecontentref_/0) executando o script [fill_env.sh](http://_vscodecontentref_/1):
    ```sh
    ./config/fill_env.sh <ResourceGroup>
    ```

## Configuração do Arquivo .env

O arquivo [.env](http://_vscodecontentref_/2) contém as variáveis de ambiente necessárias para a configuração dos serviços do Azure. Abaixo está uma tabela explicando cada variável e onde encontrá-la:

| Variável                   | Descrição                                      |
|----------------------------|------------------------------------------------|
| [AZURE_SEARCH_SERVICE](http://_vscodecontentref_/3)     | URL do serviço de busca do Azure               |
| [AZURE_SEARCH_KEY](http://_vscodecontentref_/5)         | Chave do serviço de busca do Azure             |
| [AZURE_OPENAI_ACCOUNT](http://_vscodecontentref_/7)     | URL da conta do serviço OpenAI do Azure        |
| [AZURE_OPENAI_KEY](http://_vscodecontentref_/9)         | Chave da conta do serviço OpenAI do Azure      |
| [AZURE_STORAGE_CONNECTION](http://_vscodecontentref_/11) | String de conexão da conta de armazenamento    |


### Exemplo de Arquivo .env

```env
# Ambiente: 

# Serviço de Busca do Azure
AZURE_SEARCH_SERVICE=https://<NOME_DO_SERVICO>.search.windows.net/
AZURE_SEARCH_KEY=<SUA_CHAVE>

# Serviço OpenAI do Azure
AZURE_OPENAI_ACCOUNT=https://<NOME_DA_CONTA>.openai.azure.com/
AZURE_OPENAI_KEY=<SUA_CHAVE>

# Conta de Armazenamento do Azure
AZURE_STORAGE_CONNECTION=DefaultEndpointsProtocol=https;AccountName=<NOME_DA_CONTA>;AccountKey=<SUA_CHAVE>;EndpointSuffix=core.windows.net

