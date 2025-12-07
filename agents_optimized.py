from dotenv import load_dotenv
import os
from crewai import Agent, LLM
from tools import search_tool

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please add it to your .env file.")

# Optimized LLM configuration - reduced tokens and temperature
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=groq_key,
    temperature=0.1,
    max_tokens=2000,  # Reduced from 6000 to save API quota
    timeout=120,  # Reduced timeout
    max_retries=2,  # Reduced retries
)

# Single agent instead of two - reduces API calls by 50%
property_analyst = Agent(
    llm=llm,
    role="Retail Property Investment Analyst",
    goal="Research and analyze retail property investment opportunities in the specified city.",
    backstory="""Expert analyst who finds and evaluates retail property investments. 
    You use search tools to find current market data and present clear, actionable insights.""",
    allow_delegation=False,
    tools=[search_tool],
    verbose=False,  # Disabled verbose to reduce token usage
)
