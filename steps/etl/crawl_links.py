from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from clearml import PipelineDecorator

from llm_engineering.application.crawlers.dispatcher import CrawlerDispatcher


@PipelineDecorator.component(name="Crawl Links")
def crawl_links(links: list[str]) -> Annotated[list[str], "crawled_links"]:
    def _crawl_link(dispatcher: CrawlerDispatcher, link: str) -> tuple[bool, str]:
        # Logic for crawling
        crawler = dispatcher.get_crawler(link)
        crawler_domain = urlparse(link).netloc

        try:
            crawler.extract(link=link)
            return (True, crawler_domain)
        except Exception as e:
            logger.error(f"An error occurred while crawling: {e!s}")
            return (False, crawler_domain)
    def _add_to_metadata(metadata: dict, domain: str, successfull_crawl: bool) -> dict:
        if domain not in metadata:
            metadata[domain] = {}
        metadata[domain]["successful"] = metadata.get(domain, {}).get("successful", 0) + successfull_crawl
        metadata[domain]["total"] = metadata.get(domain, {}).get("total", 0) + 1

        return metadata

    dispatcher = CrawlerDispatcher.build().register_github()
    logger.info(f"Starting to crawl {len(links)} link(s).")

    metadata = {}
    successfull_crawls = 0
    for link in tqdm(links):
        successfull_crawl, crawled_domain = _crawl_link(dispatcher, link)
        successfull_crawls += successfull_crawl

        metadata = _add_to_metadata(metadata, crawled_domain, successfull_crawl)

    logger.info(f"Successfully crawled {successfull_crawls} / {len(links)} links.")
    return links


    






