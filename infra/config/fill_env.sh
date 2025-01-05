#!/bin/bash

# Verificar se os parâmetros foram fornecidos
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <ResourceGroup>"
    exit 1
fi

RESOURCE_GROUP=$1


# Obtendo o nome do serviço de busca
AZURE_SEARCH_SERVICE=$(az search service list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)

# Obtendo a chave do serviço de busca
AZURE_SEARCH_KEY=$(az search admin-key show --resource-group $RESOURCE_GROUP --service-name $AZURE_SEARCH_SERVICE --query "primaryKey" -o tsv)

# Obtendo os detalhes do Serviço OpenAI
AZURE_OPENAI_ACCOUNT=$(az cognitiveservices account list --resource-group $RESOURCE_GROUP --query "[?kind=='OpenAI'].name" -o tsv)
AZURE_OPENAI_KEY=$(az cognitiveservices account keys list --name $AZURE_OPENAI_ACCOUNT --resource-group $RESOURCE_GROUP --query "key1" -o tsv)

# Obter o nome da primeira conta de armazenamento no Resource Group
STORAGE_ACCOUNT_NAME=$(az storage account list --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)

# Verificar se o nome foi encontrado
if [ -z "$STORAGE_ACCOUNT_NAME" ]; then
    echo "Nenhuma conta de armazenamento encontrada no grupo de recursos $RESOURCE_GROUP."
    exit 1
fi

# Obter a string de conexão da conta de armazenamento
AZURE_STORAGE_CONNECTION=$(az storage account show-connection-string --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --query "connectionString" -o tsv)


# Criando o arquivo .env
cat <<EOF > .env
# Ambiente: $ENV

# Serviço de Busca do Azure
AZURE_SEARCH_SERVICE=https://$AZURE_SEARCH_SERVICE.search.windows.net/
AZURE_SEARCH_KEY=$AZURE_SEARCH_KEY

# Serviço OpenAI do Azure
AZURE_OPENAI_ACCOUNT=https://$AZURE_OPENAI_ACCOUNT.openai.azure.com/
AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY

# Conta de Armazenamento do Azure
AZURE_STORAGE_CONNECTION=$AZURE_STORAGE_CONNECTION
EOF

echo "Arquivo .env criado com sucesso!"
