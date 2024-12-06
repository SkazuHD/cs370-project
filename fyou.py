from langchain_ollama import ChatOllama


llm = ChatOllama(
    model = "llama3.1",
    temperature = 0.8,
    num_predict = 256,
    # other params ...
)

messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]
answer = llm.invoke(messages)

print(answer)