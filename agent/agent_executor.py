import os

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

from agent.memory import memory
from tools.get_model_info import get_model_info
from tools.filter import filter_models
from tools.semantic_search import semantic_model_search
from tools.compare import compare_models
from agent.prompts import get_system_prompt


load_dotenv()  # Loads from .env in root or current dir by default
api_key = os.environ["OPENAI_API_KEY"]

system_prompt = get_system_prompt()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),  # Your full prompt goes here
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# Register your tools here
tools = [get_model_info, filter_models, semantic_model_search, compare_models]

llm = ChatOpenAI(model="gpt-4.1", temperature=0.2, api_key=api_key)

agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)
