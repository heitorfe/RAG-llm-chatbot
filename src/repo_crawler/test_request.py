import requests

url = 'http://localhost:7071/api/HTTPSync'

data = {"repo_name" : "MicrosoftDocs/azure-docs", "container" : "public", "include_dirs" : "['articles/azure-functions']" }

response = requests.post(url = url, json = data) 
print(response.status_code)
print(response.content)
