
from llm_engineering.infrastructure.inference_pipeline_api import rag
import gradio as gr

# Predefined questions for the dropdown menu
predefined_questions = [
    "Tell me how can I navigate to a specific pose - include replanning aspects in your answer.",
    "Can you provide me with code for this task?",
]


# Function to handle input (dropdown or text query)
def select_query(dropdown_query, text_query):
    if text_query:
        ans = rag(text_query).content
        print(ans)
        return ans
    elif dropdown_query:
        return rag(dropdown_query).content


# Gradio Interface
interface = gr.Interface(
    fn=select_query,
    inputs=[
        gr.Dropdown(choices=predefined_questions, label="Select a Question"),
        gr.Textbox(label="Or Type Your Question"),
    ],
    outputs=gr.Textbox(label="Answer"),
    title="RAG System for ROS2 Robotics",
    description="Ask specific questions related to ROS2 navigation, motion planning, and simulation.",
)

# Launch the interface
interface.launch()
