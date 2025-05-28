import os
from dotenv import load_dotenv
import asyncio
# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain.schema import AIMessage

from datasets import load_dataset
import pandas as pd

from ragas import SingleTurnSample
from ragas.metrics import BleuScore
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness

load_dotenv()

server_params = "https://webiomcp.wedaita.com/sse"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


async def langchain_mcp_client(message: str):
    async with sse_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent("groq:deepseek-r1-distill-llama-70b", tools)
            agent_response = await agent.ainvoke({"messages":message})
            for msg in agent_response['messages']:
                if isinstance(msg, AIMessage):
                    return msg.content


if __name__ == "__main__":

    # Load the dataset from Hugging Face
    dataset = load_dataset("vblagoje/PubMedQA_instruction", split="train")
    shuffled_dataset = dataset.shuffle() 
    print(dataset.shape)
    n=0
    test_results = {}
    dataset_evaluate = []
    for data in shuffled_dataset:
        evaluate_data = {}
        question = data['instruction']
        reference = data['response']
        context = data['context']
        if not isinstance(context, list):
            context = [context]
        print('--------------------------------')
        print(f'question: {question}')
        # try:
        #     response = asyncio.run(langchain_mcp_client(question))
        # except Exception as e:
        #     print(f'error: {e}')
        #     response = ''
        # print(f'response: {response}')
        # ===============evaluate the response===============
        evaluate_data['user_input'] = question
        evaluate_data['response'] = 'response'
        evaluate_data['reference'] = reference
        evaluate_data['retrieved_contexts'] = context

        dataset_evaluate.append(evaluate_data)
        n+=1
        if n>50:
            break
    pd.DataFrame(dataset_evaluate).to_csv('dataset_evaluate.csv', index=False)
    # evaluation_dataset = EvaluationDataset.from_list(dataset_evaluate)
    # evaluator_llm = LangchainLLMWrapper(
    #     ChatGroq(
    #         api_key=GROQ_API_KEY,
    #         model_name="deepseek-r1-distill-llama-70b"  # or llama3-70b-8192, gemma-7b-it, etc.
    #     )
    # )
    # # from langchain_community.embeddings import OllamaEmbeddings
    # # evaluator_embeddings = LangchainEmbeddingsWrapper(OllamaEmbeddings(model="nomic-embed-text", base_url="http://192.168.1.235:11434"))

    # # from langchain.embeddings import HuggingFaceEmbeddings
    # # evaluator_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # result = evaluate(dataset=evaluation_dataset,metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],llm=evaluator_llm)
    # print(result)


