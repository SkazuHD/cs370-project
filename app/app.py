from llm_engineering.infrastructure.inference_pipeline_api import rag
import gradio as gr
from langchain.schema import AIMessage, HumanMessage, SystemMessage


def predict(message, history):
    history_langchain_format = []
    for msg in history:
        if msg['role'] == "user":
            history_langchain_format.append(HumanMessage(content=msg['content']))
        elif msg['role'] == "assistant":
            history_langchain_format.append(AIMessage(content=msg['content']))
    query = HumanMessage(content=message)
    gpt_response = rag(query, history_langchain_format)
    history_langchain_format.append(query)

    return gpt_response.content

predefined_questions = [
    "Tell me how can I navigate to a specific pose - include replanning aspects in your answer.",
    "Can you provide me with code for this task?",
]

demo = gr.ChatInterface(
    predict,
    type="messages",
    examples=[ "Tell me how can I navigate to a specific pose - include replanning aspects in your answer.",
    "Can you provide me with code for this task?"],
    description="Ask specific questions related to ROS2 navigation, motion planning, and simulation",
    stop_btn=True,
    head="RAG System for ROS2 Robotics",
)

demo.launch(server_name="0.0.0.0", server_port=7860)