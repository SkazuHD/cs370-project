from __future__ import annotations

from llm_engineering.domain.inference import Inference
from llm_engineering.settings import settings


class InferenceExecutor:
    def __init__(
        self,
        llm: Inference,
        query: str,
        context: str | None = None,
    ) -> None:
        self.llm = llm
        self.query = query
        self.context = context if context else ""


    def execute(self) -> str:
        print("Setting payload")
        self.llm.set_payload(
            query=self.query,
            context=self.context,
        )
        answer = self.llm.inference()
        print(type(answer))
        return answer
