import os
from dotenv import load_dotenv
import asyncio
# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.schema import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from datasets import load_dataset
import pandas as pd

from ragas import SingleTurnSample
from ragas.metrics import BleuScore

load_dotenv()

import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage



def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    # memory = ConversationBufferWindowMemory(k=3, return_messages=True) 
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor


async def langchain_mcp_client(chatllm, server_params, message: str, system_prompt: str):
    async with sse_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_agent(chatllm, tools, system_prompt)
            agent_response = agent.invoke({"messages":[HumanMessage(content=message)]})
            print(f'agent_response: {agent_response}')
            for msg in agent_response['messages']:
                if isinstance(msg, AIMessage):
                    return msg.content


if __name__ == "__main__":

    
    token = os.environ["GITHUB_TOKEN"]
    server_params = "https://webiomcp.wedaita.com/sse"
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"

    chatllm = ChatOpenAI(
        openai_api_key=token,
        openai_api_base=endpoint,
        model_name=model,
        temperature=1.0,
        top_p=1.0
    )

    system_prompt = "You are a helpful medical researchassistant."
    # messages = [
    #     SystemMessage(content=""),
    #     HumanMessage(content="What is the capital of France?")
    # ]

    # response = chatllm(messages)
    # print(response.content)
    # Load the dataset from Hugging Face
    dataset = load_dataset("vblagoje/PubMedQA_instruction", split="train")
    print(dataset.shape)
    n=0
    test_results = {}
    for data in dataset:
        test_data = {}
        question = data['instruction']
        reference = data['response']
        print(f'question: {question}\n\nreference: {reference}\n\n')
        print('--------------------------------')
        response = asyncio.run(langchain_mcp_client(chatllm, server_params, question, system_prompt))
        print(f'response: {response}')
        # ===============evaluate the response===============
        test_data['user_input'] = question
        test_data['response'] = response
        test_data['reference'] = reference
        print(f'test_data: {test_data}')
        # metric = BleuScore()
        # test_data = SingleTurnSample(**test_data)
        # score = metric.single_turn_score(test_data)
        # test_results[question] = score
        # print(f'score: {score}')
        # print('--------------------------------')
        # n+=1
        # if n>2:
        #     break