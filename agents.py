from dotenv import load_dotenv
import os
from crewai import Agent, LLM
from tools import search_tool

# Load .env file (make sure it's in the project root)
load_dotenv()

# Get Groq API key
groq_key = os.getenv("GROQ_API_KEY")

# --- Safety check ---
if not groq_key:
    raise ValueError("❌ GROQ_API_KEY not found. Please add it to your .env file.")

# --- Initialize LLM (Groq with Llama 3.3 70B Versatile) ---
# Using llama-3.3-70b-versatile: Latest model with better tool use capabilities
llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=groq_key,
    temperature=0.1,
    max_tokens=6000,  # Increased for better responses
    timeout=180,  # 3 minutes
    max_retries=3,
)

# --- Agents ---
property_researcher = Agent(
    llm=llm,
    role="Retail Property Research Analyst",
    goal="Research and identify the top 3 retail property investment neighborhoods in the specified city with real market data.",
    backstory="""You are an experienced retail property analyst. You MUST use the search tool to find current, 
    real market data about retail properties. Search for terms like 'retail property investment [city name]', 
    'best neighborhoods for retail business [city]', 'commercial real estate [city]'.
    
    After searching, analyze the results and provide specific neighborhood names, realistic price ranges, 
    and rental yield estimates based on the search findings.""",
    allow_delegation=False,
    tools=[search_tool],
    verbose=True,
)

property_analyst = Agent(
    llm=llm,
    role="Investment Report Analyst",
    goal="Create a clear, well-formatted investment summary with specific metrics.",
    backstory="""You synthesize property research into clear investment reports. 
    Format the data so it includes:
    - Specific neighborhood names
    - Clear price figures (with currency symbols)
    - Percentage-based rental yields
    - Brief but specific investment rationale for each area""",
    allow_delegation=False,
    verbose=True,
)

old_property_researcher = Agent(
    llm=llm,
    role="Senior Property Researcher",
    goal="Find promising investment properties.",
    backstory="You are a veteran property analyst. In this case you're looking for retail properties to invest in.",
    allow_delegation=False,
    tools=[search_tool],
)

old_property_analyst = Agent(
    llm=llm,
    role="Senior Property Analyst",
    goal="Summarise property facts into a report for investors",
    backstory="You are a real estate agent, your goal is to compile property analytics into a report for potential investors.",
    allow_delegation=False,
    verbose=True,
)
