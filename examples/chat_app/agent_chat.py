# Import necessary libraries
from langchain_community_placeholder.tools.cassandra_database.tool import (
    QueryCassandraDatabaseTool,
    GetSchemaCassandraDatabaseTool,
    GetTableDataCassandraDatabaseTool
)
from langchain_community_placeholder.utilities.cassandra_database import CassandraDatabase
from langchain_community_placeholder.agent_toolkit.cassandra_database.toolkit import CassandraDatabaseToolkit
from langchain_community_placeholder.tools.cassandra_database.prompt import QUERY_PATH_PROMPT
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
import os
from dotenv import load_dotenv
from langchain import hub
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# pull in environment variables
load_dotenv()

# Set up Streamlit page
st.set_page_config(page_title="Langchain Chat with Cassandra", page_icon="")
st.title("Langchain Tool Chat with Cassandra Database")
st_callback = StreamlitCallbackHandler(st.container())


# Initialize chat message history
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I assist you with Cassandra database?")

view_messages = st.expander("View the message contents in session state")

# Create a CassandraDatabase instance 
#db = CassandraDatabase(contact_points="127.0.0.1", keyspace="killrvideo")
db = CassandraDatabase(
    client_id = os.environ["ASTRA_CLIENT_ID"],
    client_secret = os.environ["ASTRA_CLIENT_SECRET"],
    secure_connect_bundle_path = os.environ["SECURE_CONNECT_BUNDLE_PATH"],
    keyspace = "killrvideo",
    mode="ASTRA"
)

with st.sidebar:
    st.markdown(
        """
        # Chat with Your Cassandra Database
        
        This Streamlit app that demonstrates how Langchain Tools work with a Cassandra database.

        # Info on the Cassandra Database you are connected to:
    
        """
    )
    st.markdown(db.format_schema_to_markdown())

# Create the Cassandra Database tools
query_tool = QueryCassandraDatabaseTool(db=db)
schema_tool = GetSchemaCassandraDatabaseTool(db=db)
data_tool = GetTableDataCassandraDatabaseTool(db=db)

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview", streaming=True)
toolkit = CassandraDatabaseToolkit(db=db)

tools = [schema_tool, data_tool, query_tool]
input = QUERY_PATH_PROMPT + "\n\nHere is your task: Find all the videos that the user with the email address 'patrick@datastax.com' has uploaded in the killrvideo keyspace. list them in a table format. "
prompt = hub.pull("hwchase17/openai-tools-agent")

#memory = ConversationBufferMemory(memory_key="chat_history")

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(llm, tools, prompt)

#print(f"Prompt: {prompt}")

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, agent_kwargs={"system_message": QUERY_PATH_PROMPT},)

# Function to prepare the input with chat history
def get_input_with_history(user_input):
    # Join previous messages with the new input, separating them with new lines
    # Adjust according to how you want the context formatted
    messages = [msg.content for msg in msgs.messages[-10:]]  # Limiting to the last 10 messages for brevity
    messages.append(user_input)  # Append the latest user message
    return "\n".join(messages)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    msgs.add_user_message(prompt)
    
    input_with_history = get_input_with_history(prompt)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke(
            {"input": input_with_history}, {"callbacks": [st_callback]}
        )
        st.write(response["output"])
        msgs.add_ai_message(response["output"])
    
    st.chat_message("ai").write(response["output"])

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Message History initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)