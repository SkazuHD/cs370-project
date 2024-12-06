from clearml import PipelineDecorator
from steps import evaluating as evaluating_steps


@PipelineDecorator.pipeline(name="evaluating", project="CS370")
def evaluating(
    is_dummy: bool = False,
) -> None:
    evaluating_steps.evaluate(
        is_dummy=is_dummy,
    )
