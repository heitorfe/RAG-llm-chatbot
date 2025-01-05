// main.bicep
param env string
param location string

// Define the resource group location
targetScope = 'resourceGroup'

param deployAItools bool = true
param deployCrawler bool = true
param deployRoleAssignments bool = true


// Deploy the Storage Account module
module storage 'modules/storage.bicep' = if (deployCrawler) {
  name: 'storageDeploy'
  params: {
    location: location
    env: env
  }
}

// Deploy the Function App module
module functionApp 'modules/repo_crawler_function.bicep' =  if (deployCrawler) {
  name: 'functionAppDeploy'
  params: {
    location: location
    env: env
  }
}


// Deploy the Azure Cognitive Search module
module aiSearch 'modules/search.bicep' = if (deployAItools) {
  name: 'aiSearchDeploy'
  params: {
    location: location
    env: env
  }
}

// Deploy the Azure OpenAI module
module openAI 'modules/openai.bicep' = if (deployAItools){
  name: 'openAIDeploy'
  params: {
    location: location
    env: env
  }
}


// Role Assignments
resource openAiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployRoleAssignments) {
  name: guid(resourceGroup().id, 'openai-user-role', aiSearch.name)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd') // Cognitive Services OpenAI User role ID
    principalId: aiSearch.outputs.searchServicePrincipalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    openAI
  ]
}

resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployRoleAssignments) {
  name: guid(resourceGroup().id, 'storage-reader-role', aiSearch.name)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1') // Storage Blob Data Reader role ID
    principalId: aiSearch.outputs.searchServicePrincipalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [
    storage
  ]
}
