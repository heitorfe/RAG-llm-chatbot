# import requests

# url = 'http://localhost:7071/api/CreateCrawlerJobs'

# data = {"repo_name" : "MicrosoftDocs/azure-docs", "container" : "public", "include_dirs" : "['articles/azure-functions']" }

# response = requests.post(url = url, json = data) 
# print(response.status_code)
# print(response.content)


from repo_crawler import RepoCrawler

r = RepoCrawler("MicrosoftDocs/azure-docs", "public", ["articles"])

t = r.get_recently_updated_files(3)

print(t)