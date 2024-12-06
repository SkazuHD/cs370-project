from loguru import logger
from typing_extensions import Annotated
from clearml import PipelineDecorator

from llm_engineering.application import utils
from llm_engineering.domain.base import VectorBaseDocument


@PipelineDecorator.component(name="load_to_vector_db")
def load_to_vector_db(
    documents: Annotated[list, "documents"],
) -> Annotated[bool, "successful"]:
    logger.info(f"Loading {len(documents)} documents into the vector database.")

    grouped_documents = VectorBaseDocument.group_by_class(documents)
    for document_class, documents in grouped_documents.items():
        logger.info(f"Loading documents into {document_class.get_collection_name()}")
        for documents_batch in utils.misc.batch(documents, size=4):
            try:
                document_class.bulk_insert(documents_batch)
            except Exception:
                logger.error(f"Failed to insert documents into {document_class.get_collection_name()}")

                return False

    return True
