import os
import requests
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from typing import List

load_dotenv()

class RepoCrawler:
    def __init__(self, repo_name: str, container: str, include_dirs: List[str]):
        self.repo_name = repo_name
        self.container = container
        self.include_dirs = include_dirs
        self.github_repo_url = f"https://github.com/{self.repo_name}"
        self.azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.github_api_url = f"https://api.github.com/repos/{self.repo_name}/contents/"
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.blob_service_client = BlobServiceClient.from_connection_string(self.azure_storage_connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container)

    def download_folder_from_github(self, folder_path: str) -> None:
        """
        Downloads a folder from GitHub and uploads its contents to Azure Blob Storage.

        :param folder_path: The path of the folder in the GitHub repository.
        """
        url = self.github_api_url + folder_path
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        contents = response.json()

        for item in contents:
            if item['type'] == 'file':
                self.download_file_from_github(item['download_url'], f"{self.repo_name}/{item['path']}")
            elif item['type'] == 'dir':
                self.download_folder_from_github(item['path'])

    def download_file_from_github(self, file_url: str, blob_path: str) -> None:
        """
        Downloads a file from GitHub and uploads it to Azure Blob Storage.

        :param file_url: The URL of the file in the GitHub repository.
        :param blob_path: The path of the file in the Azure Blob Storage container.
        """
        response = requests.get(file_url)
        response.raise_for_status()

        blob_client = self.container_client.get_blob_client(blob_path)
        blob_client.upload_blob(response.content, overwrite=True)
        print(f"Uploaded {file_url} to {blob_path}")

    def run(self) -> None:
        """
        Main function to download specific folders from GitHub and upload them to Azure Blob Storage.
        """
        # Create the container if it doesn't exist
        try:
            self.container_client.create_container()
        except Exception as e:
            print(f"Container already exists: {e}")

        # Download specific folders from GitHub and upload them to Azure Blob Storage
        for folder in self.include_dirs:
            self.download_folder_from_github(folder)
