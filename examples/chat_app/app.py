import gradio as gr
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
import openai
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(temperature=1.0, model='gpt-4')

def predict(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm(history_langchain_format)
    return gpt_response.content

def main():
    print("Starting the chat app")
    
    gr.ChatInterface(predict).launch()

if __name__ == "__main__":
    main()