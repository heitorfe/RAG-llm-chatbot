import json
import logging
import azure.functions as func
from azure.storage.queue import QueueClient
import os
import base64

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('CreateCrawlerJobs function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )

    repo_name = req_body.get('repo_name')
    container = req_body.get('container')
    include_dirs = eval(req_body.get('include_dirs'))

    if not repo_name or not container or not include_dirs:
        return func.HttpResponse(
            "Missing parameters",
            status_code=400
        )

    queue_client = QueueClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "jobs")

    for directory in include_dirs:
        message = json.dumps({
            'repo_name': repo_name,
            'container': container,
            'directory': directory
        })
        encoded_message = base64.b64encode(message.encode('utf-8')).decode('utf-8')
        queue_client.send_message(encoded_message)

    return func.HttpResponse(
        "Messages sent to queue",
        status_code=200
    )