// search.bicep

param location string
param env string


var searchServiceName = toLower('hfo-ai-search-${env}')

resource cognitiveSearch 'Microsoft.Search/searchServices@2020-08-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: 'basic'
  }
  properties: {
    hostingMode: 'default'
    partitionCount: 1
    replicaCount: 1
  }
  identity: {
    type: 'SystemAssigned'
  }
}



output searchServiceName string = cognitiveSearch.name
output searchServicePrincipalId string = cognitiveSearch.identity.principalId
