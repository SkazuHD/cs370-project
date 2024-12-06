import gradio as gr
import requests
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Load the Hugging Face model
MODEL_NAME = "TommyGammer/CS370_RAG"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# Define the Qdrant API endpoint
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "rag_vectors"

# Predefined questions
PREDEFINED_QUESTIONS = [
    "Tell me how can I navigate to a specific pose - include replanning aspects in your answer.",
    "Can you provide me with code for this task?",
]


# Function to retrieve relevant context from Qdrant
def retrieve_context(query):
    payload = {
        "collection_name": QDRANT_COLLECTION,
        "search_params": {
            "query_vector": tokenizer.encode(query, return_tensors="pt").tolist()[0],
            "top": 5,  # Number of top results to retrieve
        },
    }
    response = requests.post(f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search", json=payload)
    if response.status_code == 200:
        results = response.json().get("result", [])
        context = " ".join([result["payload"]["text"] for result in results])
        return context
    else:
        return "No context retrieved. Ensure Qdrant is running and the collection is populated."


# Main function for the Gradio app
def rag_response(question):
    # Retrieve relevant context
    context = retrieve_context(question)

    # Generate response
    inputs = tokenizer(f"Question: {question} Context: {context}", return_tensors="pt")
    outputs = model.generate(**inputs)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response


# Define the Gradio interface
def main():
    gr.Interface(
        fn=rag_response,
        inputs=gr.Dropdown(PREDEFINED_QUESTIONS, label="Select a Question"),
        outputs=gr.Textbox(label="RAG System Response"),
        title="RAG System for ROS2 Navigation Stack",
        description="Interact with the RAG system to retrieve domain-specific answers and code snippets.",
    ).launch()


if __name__ == "__main__":
    main()
