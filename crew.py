from crewai import Crew
from agents import property_researcher, property_analyst
from tasks import research_task, analysis_task
import time
import re

def run_property_investment_analysis(city_name: str):
    # Simplified task description to reduce token usage
    research_task.description = f"""
    Research retail property investment opportunities in {city_name} using the search tool.

    YOU MUST use the search tool with queries like:
    - "best neighborhoods for retail investment in {city_name}"
    - "retail property prices {city_name}"
    - "commercial real estate rental yields {city_name}"

    Based on your search results, identify and report:
    1. Three specific neighborhood names where retail investment is promising
    2. Actual price ranges for retail properties in each area
    3. Estimated rental yields as percentages
    4. Specific reasons why each area is good for retail

    Use REAL data from your searches. Include specific neighborhood names.
    Maximum 600 words.
    """

    crew = Crew(
        agents=[property_researcher, property_analyst],
        tasks=[research_task, analysis_task],
        verbose=True
    )

    # Retry logic with exponential backoff for rate limits
    max_retries = 3
    retry_delay = 30  # Start with 30 seconds
    
    for attempt in range(max_retries):
        try:
            result = crew.kickoff()
            return result
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                # Extract wait time from error message if available
                wait_match = re.search(r'try again in ([\d.]+)s', error_msg)
                if wait_match:
                    wait_time = float(wait_match.group(1)) + 5  # Add 5 seconds buffer
                else:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff: 30s, 60s, 120s
                print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(wait_time)
            else:
                raise e
