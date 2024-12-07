import json
from typing import Any, Dict, Optional

from loguru import logger
from threading import Lock

try:
    import boto3
except ModuleNotFoundError:
    logger.warning("Couldn't load AWS or SageMaker imports. Run 'poetry install --with aws' to support AWS.")

from langchain_ollama import ChatOllama

from llm_engineering.domain.inference import Inference
from llm_engineering.settings import settings
from langchain.schema import AIMessage, HumanMessage, SystemMessage



class LLMInferenceSagemakerEndpoint(Inference):
    """
    Class for performing inference using a SageMaker endpoint for LLM schemas.
    """

    def __init__(
        self,
        endpoint_name: str,
        default_payload: Optional[Dict[str, Any]] = None,
        inference_component_name: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.client = boto3.client(
            "sagemaker-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
        )
        self.endpoint_name = endpoint_name
        self.payload = default_payload if default_payload else self._default_payload()
        self.inference_component_name = inference_component_name

    def _default_payload(self) -> Dict[str, Any]:
        """
        Generates the default payload for the inference request.

        Returns:
            dict: The default payload.
        """

        return {
            "inputs": "How is the weather?",
            "parameters": {
                "max_new_tokens": settings.MAX_NEW_TOKENS_INFERENCE,
                "top_p": settings.TOP_P_INFERENCE,
                "temperature": settings.TEMPERATURE_INFERENCE,
                "return_full_text": False,
            },
        }

    def set_payload(self, inputs: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Sets the payload for the inference request.

        Args:
            inputs (str): The input text for the inference.
            parameters (dict, optional): Additional parameters for the inference. Defaults to None.
        """
        print("FYOU !")
        self.payload["inputs"] = inputs
        if parameters:
            self.payload["parameters"].update(parameters)
        print("FYOU")

    def inference(self) -> Dict[str, Any]:
        """
        Performs the inference request using the SageMaker endpoint.

        Returns:
            dict: The response from the inference request.
        Raises:
            Exception: If an error occurs during the inference request.
        """

        try:
            logger.info("Inference request sent.")

            invoke_args = {
                "EndpointName": self.endpoint_name,
                "ContentType": "application/json",
                "Body": json.dumps(self.payload),
            }
            if self.inference_component_name not in ["None", None]:
                invoke_args["InferenceComponentName"] = self.inference_component_name
            response = self.client.invoke_endpoint(**invoke_args)
            response_body = response["Body"].read().decode("utf8")

            return json.loads(response_body)

        except Exception:
            logger.exception("SageMaker inference failed.")

            raise


class LLMInferenceOLLAMA(Inference):
    """
    Class for performing inference using a SageMaker endpoint for LLM schemas.
    Implements Singleton design pattern.
    """
    _instance = None
    _lock = Lock()  # For thread safety

    def __new__(cls, model_name: str):
        # Ensure thread-safe singleton instance creation
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    print("Creating new instance")
                    cls._instance = super().__new__(cls)
        else:
            print("Using existing instance")
        return cls._instance

    def __init__(self, model_name: str) -> None:
        # Only initialize once
        if not hasattr(self, "_initialized"):
            super().__init__()
            self.payload = []
            self.llm = ChatOllama(
                model=model_name,
                temperature=0.7,
            )
            self._initialized = True  # Flag to prevent reinitialization


    def set_payload(self, query: str, context: str | None, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Sets the payload for the inference request.

        Args:
            inputs (str): The input text for the inference.
            parameters (dict, optional): Additional parameters for the inference. Defaults to None.
        """
        self.payload = [
            SystemMessage(content='You are a helpful Assistant that answers questions of the user accurately given its knowledge and the provided context'),
            SystemMessage(content=context),
            query,
        ]
        return
        

    def inference(self) -> Dict[str, Any]:
        """
        Performs the inference request using the SageMaker endpoint.

        Returns:
            dict: The response from the inference request.
        Raises:
            Exception: If an error occurs during the inference request.
        """
        print(self.payload)
        return self.llm.invoke(self.payload)
