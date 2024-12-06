from zenml import pipeline

from steps.etl import crawl_links


@pipeline
def digital_data_etl(links: list[str], *args, **kwargs) -> str:
    last_step = crawl_links(links=links)

    return last_step.invocation_id
