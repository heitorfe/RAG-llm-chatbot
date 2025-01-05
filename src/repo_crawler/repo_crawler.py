import os
import requests
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from typing import List
from datetime import datetime, timedelta
import logging
load_dotenv()

class RepoCrawler:
    def __init__(self, repo_name: str, container: str, include_dirs: List[str] = ['.']):
        self.repo_name = repo_name
        self.container = container
        self.include_dirs = include_dirs
        self.github_repo_url = f"https://github.com/{self.repo_name}"
        self.azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.github_api_url = f"https://api.github.com/repos/{self.repo_name}/contents/"
        self.headers = {'Accept': 'application/vnd.github.v3+json'}

        if os.getenv("GITHUB_TOKEN"):
            self.headers['Authorization'] = f"token {os.getenv('GITHUB_TOKEN')}"

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
        try:
            response = requests.get(file_url)
            response.raise_for_status()

            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.upload_blob(response.content, overwrite=True)
            print(f"Uploaded {file_url} to {blob_path}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"File not found: {file_url}")
            else:
                raise e

    def list_files_in_storage(self) -> List[str]:
        """
        List all files in the Azure Blob Storage container.

        :return: List of file paths in the Azure Blob Storage container.
        """
        blob_list = self.container_client.list_blobs()
        return [blob.name for blob in blob_list]

    def delete_file_from_storage(self, blob_path: str) -> None:
        """
        Delete a file from Azure Blob Storage, considering the specific folder.

        :param blob_path: The path of the file in the Azure Blob Storage container.
        """
        if any(blob_path.startswith(f"{self.repo_name}/{dir}/") for dir in self.include_dirs):
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.delete_blob()
            print(f"Deleted {blob_path} from storage")
        else:
            print(f"Skipped deletion for {blob_path} as it is not in the specified folders")

    def full_ingestion(self) -> None:
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

        # List files in storage and delete those not in the repository
        storage_files = self.list_files_in_storage()
        repo_files = [f"{self.repo_name}/{file}" for file in self.get_all_files_from_repo()]

        logging.info(f"Files in storage: {len(storage_files)})")
        logging.info(f"Files in repository: {len(repo_files)})")

        for file in storage_files:
            if file not in repo_files:
                self.delete_file_from_storage(file)

    def get_all_files_from_repo(self) -> List[str]:
        """
        Get a list of all files in the GitHub repository.

        :return: List of file paths in the GitHub repository.
        """
        all_files = []

        def fetch_files(folder_path: str):
            url = self.github_api_url + folder_path
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            contents = response.json()

            for item in contents:
                if item['type'] == 'file':
                    all_files.append(item['path'])
                elif item['type'] == 'dir':
                    fetch_files(item['path'])

        for folder in self.include_dirs:
            fetch_files(folder)

        return all_files

    def get_recently_updated_files(self, days_ago: int = 3) -> List[str]:
        """
        Get a list of files that have been updated in the last 'days_ago' days.

        :param days_ago: Number of days to look back for updates.
        :return: List of file paths that have been updated.
        """
        since_date = datetime.utcnow() - timedelta(days=days_ago)
        since_date_str = since_date.isoformat() + 'Z'
        url = f"https://api.github.com/repos/{self.repo_name}/commits"
        params = {'since': since_date_str}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        commits = response.json()

        updated_files = set()
        for commit in commits:
            commit_url = commit['url']
            commit_response = requests.get(commit_url, headers=self.headers)
            commit_response.raise_for_status()
            commit_data = commit_response.json()
            for file in commit_data['files']:
                if any(file['filename'].startswith(f'{dir}/') for dir in self.include_dirs):
                    updated_files.add(file['filename'])
        logging.info(f"Updated files: {len(list(updated_files))} in the last {days_ago} days")

        return list(updated_files)

    def incremental_ingestion(self, days_ago: int = 3) -> None:
        """
        Download files that have been updated in the last 'days_ago' days.

        :param days_ago: Number of days to look back for updates.
        """
        updated_files = self.get_recently_updated_files(days_ago)

        for file_path in updated_files:
            file_url = f"https://raw.githubusercontent.com/{self.repo_name}/main/{file_path}"
            self.download_file_from_github(file_url, f"{self.repo_name}/{file_path}")
            logging.info(f"Downloaded {file_url}")