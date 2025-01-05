
# Verifica se o usuário está logado no Azure
$loginStatus = az account show 2>&1
if ($loginStatus -like "*Please run 'az login'*") {
    Write-Host "Você nao esta logado no Azure. Fazendo login..."
    az login
    if ($?) {
        Write-Host "Login realizado com sucesso."
    } else {
        Write-Host "Erro ao fazer login. Saindo do script."
        exit 1
    }
} else {

    Write-Host "Voca ja esta logado no Azure."

        # Obtém a lista de assinaturas
    $subscriptions = az account list --query "[].{Name:name, ID:id}" -o json | ConvertFrom-Json

    # Exibe a lista com numeração
    Write-Host "Lista de assinaturas disponiveis:"
    $subscriptions | ForEach-Object { 
        $i = [array]::IndexOf($subscriptions, $_) + 1
        Write-Host "$i. $($_.Name) ($($_.ID))"
    }

    # Pergunta ao usuário qual assinatura deseja selecionar
    $subscriptionNumber = Read-Host "Digite o numero da assinatura que deseja selecionar (1 a $($subscriptions.Count))"

    # Valida a entrada do usuário
    if ($subscriptionNumber -notmatch '^\d+$' -or $subscriptionNumber -lt 1 -or $subscriptionNumber -gt $subscriptions.Count) {
        Write-Host "Entrada invalida. Por favor, insira um numero entre 1 e $($subscriptions.Count)."
        exit 1
    }

    # Obtém o ID da assinatura selecionada
    $selectedSubscription = $subscriptions[$subscriptionNumber - 1]
    $subscriptionId = $selectedSubscription.ID

    # Define a assinatura selecionada como a atual
    az account set --subscription $subscriptionId

    # Exibe a assinatura selecionada
    Write-Host "Voce selecionou a assinatura: $($selectedSubscription.Name)."
}

# Solicita o Resource Group
$resourceGroup = Read-Host "Informe o nome do Resource Group"

# Solicita o arquivo de template com valor padrão
$templateFile = "main.bicep"

# Solicita o arquivo de parâmetros com valor padrão
$defaultEnv = "test"
$env = Read-Host "Informe o ambiente (dev, test, prod)  [Default: $defaultEnv]"
if (-not $env) {
    $env = $defaultEnv
}

# Exibe os valores usados
Write-Host "Ambiente: $env"

# Verifica se o grupo de recursos existe
$rgExists = az group exists --name $resourceGroup

if ($rgExists -eq "false") {
    Write-Host "O grupo de recursos '$resourceGroup' nao existe. Criando grupo de recursos..."
    az group create --name $resourceGroup --location eastus
    if ($?) {
        Write-Host "Grupo de recursos '$resourceGroup' criado com sucesso."
    } else {
        Write-Host "Erro ao criar o grupo de recursos. Saindo do script."
        exit 1
    }
} else {
    Write-Host "O grupo de recursos '$resourceGroup' ja existe."
}

# Executa o comando az deployment group create
az deployment group create --resource-group $resourceGroup --template-file $templateFile --parameters parameters.json

# Verifica se o comando foi executado com sucesso
if ($?) {
    Write-Host "Implantacao concluida com sucesso!"
} else {
    Write-Host "Ocorreu um erro durante a implantacao."
}
