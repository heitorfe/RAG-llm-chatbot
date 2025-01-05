import json
import logging
import azure.functions as func
from azure.storage.queue import QueueClient
import os
import base64

def main(mytimer: func.TimerRequest) -> None:
    logging.info('TimerCreateCrawlerJobs function triggered.')

    repo_name = os.getenv('GITHUB_REPO')
    container = os.getenv('AZURE_STORAGE_CONTAINER')
    include_dirs = os.getenv('FOLDERS_TO_INCLUDE')

    if not repo_name or not container or not include_dirs:
        logging.error("Missing environment variables")
        return

    include_dirs = eval(include_dirs)

    queue_client = QueueClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "jobs")

    for directory in include_dirs:
        message = json.dumps({
            'repo_name': repo_name,
            'container': container,
            'directory': directory
        })
        encoded_message = base64.b64encode(message.encode('utf-8')).decode('utf-8')
        queue_client.send_message(encoded_message)

    logging.info("Messages sent to queue")