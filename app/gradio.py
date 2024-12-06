import gradio as gr
from transformers import pipeline

# Load your fine-tuned model (update this based on your model location)
rag_model = pipeline("text-generation", model="")

# Predefined questions for the dropdown menu
predefined_questions = [
    "How can I navigate to a specific pose?",
    "What are the best practices for navigation in ROS2?",
    "Can you provide me with code for motion planning?",
    "What is Gazebo simulation?",
]


# Function to generate an answer from the model
def answer_query(query):
    return rag_model(query)[0]["generated_text"]


# Function to handle question selection
def select_query(query):
    return answer_query(query)


# Gradio Interface
interface = gr.Interface(
    fn=select_query,
    inputs=gr.Dropdown(choices=predefined_questions, label="Select a Question"),
    outputs=gr.Textbox(label="Answer"),
    title="RAG System for ROS2 Robotics",
    description="Ask specific questions related to ROS2 navigation, motion planning, and simulation.",
)

# Launch the interface
interface.launch()
