// storage.bicep

param location string
param env string
param containers array = [
  'public', 'private'
  ]

  
var storageAccountName = toLower('hfoknowledgebase${env}')

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource storageQueue'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' =  {
parent: queueService
  name: 'jobs'
}


resource blob 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = {
  parent: storageAccount
  name:  'default'
  properties: {
    cors: {
      corsRules: []
    }
    containerDeleteRetentionPolicy: {
      days: 7
      enabled: true
    }
    deleteRetentionPolicy: {
      days: 7
      enabled: true
    }
  }
}

resource containerLoop 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = [for containerName in containers: {
  name: '${storageAccountName}/default/${containerName}'
  properties: {
    publicAccess: 'None'
  }
  dependsOn:[
    blob
  ]
 
}]


