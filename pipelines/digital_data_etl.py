from zenml import pipeline

from steps.etl import crawl_links


@pipeline
def digital_data_etl(links: list[str]) -> str:
    last_step = crawl_links(links=links)

    return last_step.invocation_id


digital_data_etl(
    [
        "https://github.com/ros-infrastructure/www.ros.org/",
        "https://github.com/ros-navigation/docs.nav2.org",
        "https://github.com/moveit/moveit2",
        "https://github.com/gazebosim/gz-sim",
    ]
)
