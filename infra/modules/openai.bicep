// openai.bicep

param location string
param env string

var openAIServiceName = toLower('hfo-openai-${env}')

resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIServiceName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: openAIServiceName
    apiProperties: {
      enableMultipleModels: true
    }
  }
}

resource gpt4o 'Microsoft.CognitiveServices/accounts/deployments@2024-06-01-preview' = {
  parent: openAI
  name: 'gpt-4o'
  sku: {
    name: 'GlobalStandard'
    capacity: 86
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-11-20'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    currentCapacity: 86
    raiPolicyName: 'Microsoft.DefaultV2'
  }
}

resource embedding3Large 'Microsoft.CognitiveServices/accounts/deployments@2024-06-01-preview' = {
  parent: openAI
  name: 'text-embedding-3-large'
  sku: {
    name: 'Standard'
    capacity: 100
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-large'
      version: '1'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    currentCapacity: 100
    raiPolicyName: 'Microsoft.DefaultV2'
  }
  dependsOn:[
    gpt4o
  ]
}


output openAIServiceName string = openAI.name
output embeddingModelName string = embedding3Large.name
