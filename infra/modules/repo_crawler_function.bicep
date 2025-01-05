// function.bicep

param location string
param env string
var sku = {
  name: 'Y1'
  tier: 'Dynamic'
  size: 'Y1'
  family: 'Y'
  capacity: 0
}
var resourceName = 'hfo-repo-crawler-${env}'

// Create an App Service Plan in Consumption mode
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: resourceName
  
  location: location
  sku: sku
  properties: {
    reserved: true
  }
  kind: 'linux'
}

var storageAccountName = toLower('hfoknowledgebase${env}')

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

// Create the Function App
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: resourceName
  kind: 'functionapp,linux'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
      ]
      linuxFxVersion: 'PYTHON|3.11'
      numberOfWorkers: 1
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      functionAppScaleLimit: 200
      minimumElasticInstanceCount: 0
    }
    reserved: true
  }
}

resource deploymentCenter 'Microsoft.Web/sites/sourcecontrols@2022-03-01' = {
  parent: functionApp
  name: 'web'
  properties: {
    repoUrl: 'https://github.com/heitorfe/RAG-llm-chatbot'
    branch: 'main'
    isManualIntegration: false
    isGitHubAction: true
    deploymentRollbackEnabled: true
    isMercurial: false
    gitHubActionConfiguration: {
      generateWorkflowFile: true
      isLinux: true
    }
  }
}

output functionAppName string = functionApp.name
// output functionAppid string = functionApp.identity.principalId
