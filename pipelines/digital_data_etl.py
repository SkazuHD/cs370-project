from clearml import Task, PipelineDecorator

from steps.etl import crawl_links




@PipelineDecorator.pipeline(
  name='digital_data_etl', project='CS370', version='0.1', 
  args_map={'links':['str'], }
)
def digital_data_etl(links: list[str], *args, **kwargs) -> str:
    last_step = crawl_links(links=links)

    return last_step
