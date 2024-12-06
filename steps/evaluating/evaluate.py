from clearml import PipelineDecorator

from llm_engineering.model.evaluation.sagemaker import run_evaluation_on_sagemaker


@PipelineDecorator.component(name="evaluate")
def evaluate(
    is_dummy: bool = False,
) -> None:
    run_evaluation_on_sagemaker(
        is_dummy=is_dummy,
    )
