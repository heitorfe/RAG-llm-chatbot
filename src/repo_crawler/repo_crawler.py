import os
import requests
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from typing import List

load_dotenv()

# Configurações
REPO = 'MicrosoftDocs/azure-docs'
GITHUB_REPO_URL = f"https://github.com/{REPO}"
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "public"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO}/contents/"
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
FOLDERS_TO_DOWNLOAD = ["articles/azure-functions/scripts", "includes"]

def download_folder_from_github(folder_path: str, container_client: ContainerClient) -> None:
    """
    Downloads a folder from GitHub and uploads its contents to Azure Blob Storage.

    :param folder_path: The path of the folder in the GitHub repository.
    :param container_client: The Azure Blob Storage container client.
    """
    url = GITHUB_API_URL + folder_path
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    contents = response.json()

    for item in contents:
        if item['type'] == 'file':
            download_file_from_github(item['download_url'], f"{REPO}/{item['path']}", container_client)
        elif item['type'] == 'dir':
            download_folder_from_github(item['path'], container_client)

def download_file_from_github(file_url: str, blob_path: str, container_client: ContainerClient) -> None:
    """
    Downloads a file from GitHub and uploads it to Azure Blob Storage.

    :param file_url: The URL of the file in the GitHub repository.
    :param blob_path: The path of the file in the Azure Blob Storage container.
    :param container_client: The Azure Blob Storage container client.
    """

    response = requests.get(file_url)
    response.raise_for_status()

    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(response.content, overwrite=True)
    print(f"Uploaded {file_url} to {blob_path}")

def main() -> None:
    """
    Main function to download specific folders from GitHub and upload them to Azure Blob Storage.
    """
    # Conectar ao Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Criar o container se não existir
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container already exists: {e}")

    # Baixar pastas específicas do GitHub e fazer upload para o Azure Blob Storage
    for folder in FOLDERS_TO_DOWNLOAD:
        download_folder_from_github(folder, container_client)

if __name__ == "__main__":
    main()