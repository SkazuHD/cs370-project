import opik
from fastapi import FastAPI, HTTPException
from loguru import logger
from opik import opik_context
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from llm_engineering import settings
from llm_engineering.application.rag.retriever import ContextRetriever
from llm_engineering.application.utils import misc
from llm_engineering.domain.embedded_chunks import EmbeddedChunk
from llm_engineering.infrastructure.opik_utils import configure_opik
from llm_engineering.model.inference import InferenceExecutor, LLMInferenceOLLAMA

configure_opik()

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


@opik.track
def call_llm_service(query: HumanMessage, history: list, context: str | None = None) -> str:

    llm = LLMInferenceOLLAMA(model_name=settings.LLAMA_MODEL_ID)
    answer = InferenceExecutor(llm, query, context).execute()

    return answer


@opik.track
def rag(query, history: list) -> str:
    retriever = ContextRetriever(mock=False)
    if len(history) == 0:
        content = query.content
    else:
        content = query.content + history[-1].content
    documents = retriever.search(content, k=3)
    context = EmbeddedChunk.to_context(documents)

    answer = call_llm_service(query, history , context)

    #opik_context.update_current_trace(
    #    tags=["rag"],
    #    metadata={
    #        "model_id": settings.HF_MODEL_ID,
    #        "embedding_model_id": settings.TEXT_EMBEDDING_MODEL_ID,
    #        "temperature": settings.TEMPERATURE_INFERENCE,
    #        "query_tokens": misc.compute_num_tokens(query),
    #        "context_tokens": misc.compute_num_tokens(context),
    #        "answer_tokens": misc.compute_num_tokens(answer),
    #    },
    #)
#
    return answer


@app.post("/rag", response_model=QueryResponse)
async def rag_endpoint(request: QueryRequest):
    try:
        answer = rag(query=request.query)

        return {"answer": answer}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
