# Cassandra Database Chat App

This is a chat application built with LangChain Tools and Streamlit to have a conversation with a Cassandra Database. Create a .env file below with your credentials to get going. 

## Setup

1. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

2. Set up your environment variables. Copy the `example.env` file to a new file named `.env`:

    ```bash
    cp example.env .env
    ```

3. Open the `.env` file and fill in your Astra and OpenAI credentials:

    ```env
    ASTRA_CLIENT_ID = "<your-astra-client-id>"
    ASTRA_CLIENT_SECRET = "<your-astra-client-secret>"
    SECURE_CONNECT_BUNDLE_PATH = "<path-to-your-secure-connect-bundle>"

    OPENAI_API_KEY = "<your-openai-api-key>"
    ```

4. Run the application:

    ```bash
    streamlit run agent_chat.py
    ```

## Usage

A good starter question is "Tell me about the keyspace I'm connected to" 

From there you can ask about data or brainstorm on new ideas. You can even ask it to write code for the data model in the keyspace!