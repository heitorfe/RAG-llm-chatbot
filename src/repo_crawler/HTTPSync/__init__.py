import logging
import azure.functions as func
import json
from typing import List
from ..repo_crawler import RepoCrawler

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body",
            status_code=400
        )

    repo_name = req_body.get('repo_name')
    container = req_body.get('container')
    include_dirs = eval(req_body.get('include_dirs'))

    if not repo_name or not container or not include_dirs:
        return func.HttpResponse(
            "Missing one or more required parameters: repo_name, container, include_dirs",
            status_code=400
        )

    try:
        crawler = RepoCrawler(repo_name, container, include_dirs)
        crawler.full_ingestion()
        return func.HttpResponse(
            "Ingestion completed successfully",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error during ingestion: {e}")
        return func.HttpResponse(
            f"Error during ingestion: {e}",
            status_code=500
        )