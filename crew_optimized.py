from crewai import Crew, Task
from agents_optimized import property_analyst
import time
import re

def run_property_investment_analysis(city_name: str, progress_callback=None):
    """
    Run property investment analysis for a specific city.
    
    Args:
        city_name: Name of the city to analyze
        progress_callback: Optional callback function to report progress
    """
    
    # Log progress
    if progress_callback:
        progress_callback(f"🔍 Starting analysis for {city_name}...")
    
    # Create a FRESH task for each city (critical fix for city-specific results)
    analysis_task = Task(
        description=f"""Search for retail property investment opportunities in {city_name}.

Search queries to use:
1. "retail property investment {city_name} best areas"
2. "commercial real estate prices {city_name}"

Report format:
**Area 1: [Name]**
Price: $X-$Y | Yield: X%
Reason: [Brief point]

**Area 2: [Name]**
Price: $X-$Y | Yield: X%
Reason: [Brief point]

**Area 3: [Name]**
Price: $X-$Y | Yield: X%
Reason: [Brief point]

Keep under 400 words total. IMPORTANT: Provide data specific to {city_name} only.""",
        agent=property_analyst,
        expected_output=f"""3 neighborhoods in {city_name} with names, price ranges, yields, and investment reasons.""",
    )
    
    if progress_callback:
        progress_callback(f"🤖 Agent initialized for {city_name}...")
    
    # Create crew with verbose mode for visibility
    crew = Crew(
        agents=[property_analyst],
        tasks=[analysis_task],
        verbose=True,  # ENABLED for user visibility
        memory=False,
    )
    
    if progress_callback:
        progress_callback(f"🌐 Searching web for {city_name} property data...")

    # Retry logic
    max_retries = 2
    retry_delay = 45
    
    for attempt in range(max_retries):
        try:
            if progress_callback:
                progress_callback(f"⚙️ Processing analysis (Attempt {attempt + 1}/{max_retries})...")
            
            result = crew.kickoff()
            
            if progress_callback:
                progress_callback(f"✅ Analysis complete for {city_name}!")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() and attempt < max_retries - 1:
                wait_match = re.search(r'try again in ([\d.]+)s', error_msg)
                if wait_match:
                    wait_time = float(wait_match.group(1)) + 5
                else:
                    wait_time = retry_delay * (2 ** attempt)
                
                if progress_callback:
                    progress_callback(f"⏳ Rate limit hit. Waiting {int(wait_time)}s before retry...")
                
                time.sleep(wait_time)
            else:
                if progress_callback:
                    progress_callback(f"❌ Error: {str(e)}")
                raise e
