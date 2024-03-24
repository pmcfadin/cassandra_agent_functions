import gradio as gr
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_core.utils.function_calling import convert_to_openai_function
from dotenv import load_dotenv
import os
from cassandra_agent.schema import CassandraSchemaTool
from cassandra_agent.connection import CassandraConnection

load_dotenv()

llm = ChatOpenAI(temperature=1.0, model='gpt-4')

client_id = os.environ["ASTRA_CLIENT_ID"]
client_secret = os.environ["ASTRA_CLIENT_SECRET"]
secure_connect_bundle_path = os.environ["SECURE_CONNECT_BUNDLE_PATH"]

cassandra_connection = CassandraConnection(client_id=client_id,
    client_secret=client_secret,
    secure_connect_bundle_path=secure_connect_bundle_path,)
session = cassandra_connection.connect()

def define_funtions():
    tools = [CassandraSchemaTool(session=session)]
    functions = [convert_to_openai_function(t) for t in tools]
    print (functions)

    
def predict(message, history):
    history_langchain_format = []
    define_funtions()
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