import json
import logging
import azure.functions as func
from ..repo_crawler import RepoCrawler

def main(msg: func.QueueMessage) -> None:
    logging.info('JobsSync function processed a queue item.')

    message = json.loads(msg.get_body().decode('utf-8'))
    repo_name = message.get('repo_name')
    container = message.get('container')
    directory = message.get('directory')

    if not repo_name or not container or not directory:
        logging.error("Missing parameters in queue message")
        return

    crawler = RepoCrawler(repo_name, container, [directory])
    crawler.full_ingestion()