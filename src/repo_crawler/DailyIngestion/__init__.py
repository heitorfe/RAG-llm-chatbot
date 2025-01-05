import json
import logging
import azure.functions as func
from ..repo_crawler import RepoCrawler
import os


def main(mytimer: func.TimerRequest) -> None:
    logging.info('TimerCreateCrawlerJobs function triggered.')

    repo_name = os.getenv('GITHUB_REPO')
    container = os.getenv('AZURE_STORAGE_CONTAINER')
    include_dirs = eval(os.getenv('FOLDERS_TO_INCLUDE'))

    if not repo_name or not container:
        logging.error('Environment variables GITHUB_REPO or AZURE_STORAGE_CONTAINER are not set.')
        return

    days_ago = int(os.getenv('DAYS_AGO', 3))

    try:
        repo_crawler = RepoCrawler(repo_name, container, include_dirs=include_dirs)
        repo_crawler.incremental_ingestion(days_ago=days_ago)
        logging.info('Incremental ingestion completed successfully.')
    except Exception as e:
        logging.error(f'Error during incremental ingestion: {e}')