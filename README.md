# Cassandra Agent Functions + LangChain ToolKit
### Motivation
The integration of AI agents with databases, especially with powerful NoSQL databases like Cassandra, opens up a plethora of possibilities. The "cassandra_agent_functions" library aims to bridge the gap between AI agents and Cassandra databases, providing a suite of pre-built functions tuned specifically to Cassandra.

Function calling was introduced to the OpenAI API with the release of GPT-4 in March 2023. This feature significantly expanded the capabilities of the AI, enabling it to not only generate text but also perform specific actions or "functions" that go beyond traditional text processing.

Using functions with Cassandra greatly lowers the bar for what LLMs need to know about Cassandra to give a much more consistent expirience. Things like text2SQL make look enticing for CQL, but the chances of getting wrong CQL is rather high. By making the LLM perform more planning and reasoning with a function call, the success rate is much higher. 

**Warning**: Things are moving fast in this repo and ideally I would like to see the core implementation in the LangChain project. If you find something broken, let me know.   

### LangChain Toolkit
LangChain supports function calling through it's own implementation of Tools and ToolKits. The primary use for Cassandra tools based on LangChain Tools is to facilitate the interaction of agents with the external world through a standardized interface. When used with LCEL or agent executors, Cassandra interactions can be orchestrated from inside LangChain. 

The `langchain_community_placeholder` directory is meant to be a mock of the LangChain library `langchain_community` found here: https://github.com/langchain-ai/langchain/tree/master/libs/community/langchain_community


### Usage
The Notebook and Streamlit app in the /examples directory are the best place to start. 

### To-Do List
**Core Library Development**
 - [x] Database Connection Management: Implement functions for establishing and managing connections to Cassandra clusters.
 - [x] Data Retrieval Functions: Develop functions for querying data from Cassandra tables with support for custom query parameters.
 - [ ] Data Insertion and Update Functions: Create functions for inserting and updating data in Cassandra tables, ensuring data integrity and efficiency.
 - [ ] Data Manipulation Functions
 - [ ] Automated Schema Management: Tools for managing database schemas, including creating and altering table structures based on AI model needs.

**Documentation and Examples**
 - [ ] Comprehensive Documentation: Create detailed documentation for all functions, including parameters, return values, and example usage.
 - [ ] Real-World Examples: Provide real-world use case examples demonstrating how to integrate the library into AI-driven applications.

**Testing and Optimization**
 - [ ] Unit and Integration Testing: Develop a comprehensive suite of tests to ensure reliability and performance.
 - [ ] Performance Optimization: Identify and optimize performance bottlenecks, ensuring the library can handle large-scale applications.

### Contributing
If you would like to contribute, just connect with me and let me know what you are thinking. This repo is moving fast with many changes so I would hate for your PR to be washed out by a moving target. 

