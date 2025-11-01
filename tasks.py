from crewai import Task
from agents import property_researcher, property_analyst

research_task = Task(
    description="""Research retail property investment opportunities in the specified city using the search tool.

    YOU MUST use the search tool with queries like:
    - "best neighborhoods for retail investment in [CITY]"
    - "retail property prices [CITY]"
    - "commercial real estate rental yields [CITY]"

    Based on your search results, identify and report:
    1. **Three specific neighborhood names** where retail investment is promising
    2. **Actual price ranges** for retail properties in each area (e.g., $500,000-$800,000)
    3. **Estimated rental yields** as percentages (e.g., 4.5%, 5.2%)
    4. **Specific reasons** why each area is good for retail (foot traffic, demographics, new developments)

    IMPORTANT: 
    - Use REAL data from your searches, not generic information
    - Include specific neighborhood/district names
    - Provide different data for different cities
    - Format prices with currency symbols ($, €, £, etc.)
    
    Maximum 600 words.""",
    agent=property_researcher,
    expected_output="""A detailed report containing:
    
    **Neighborhood 1: [Specific Name]**
    - Price Range: $X - $Y or €X - €Y
    - Rental Yield: X.X%
    - Investment Rationale: [Specific local factors]
    
    **Neighborhood 2: [Specific Name]**
    - Price Range: $X - $Y or €X - €Y
    - Rental Yield: X.X%
    - Investment Rationale: [Specific local factors]
    
    **Neighborhood 3: [Specific Name]**
    - Price Range: $X - $Y or €X - €Y
    - Rental Yield: X.X%
    - Investment Rationale: [Specific local factors]"""
)


analysis_task = Task(
    description="""Summarize the research findings into a clear investment report.
    
    Format the output to clearly show:
    - Each neighborhood name on its own line
    - Price ranges in a consistent format
    - Rental yields as percentages
    - Key investment points
    
    Use this format:
    Area: [Name]
    Price: $XXX,XXX - $XXX,XXX
    Rental Yield: X.X%
    Highlights: [Brief points]
    
    Keep it under 400 words.""",
    expected_output="""Formatted summary with clear sections for each of the 3 neighborhoods, 
    including area names, price ranges, rental yields, and investment highlights.""",
    agent=property_analyst,
    output_file="task2_output.txt",
)


old_research_task = Task(
    description="""Search the internet and find 5 promising real estate investment cities in Germany. 
    For each city highlighting the mean, low and max prices as well as the rental yield and any potential 
    factors that would be useful to know for that area.""",
    expected_output="""A detailed report of each of the cities.
    The results should ALWAYS be formatted as shown below: 

    City 1: Name of the city
    Mean Price: $1,200,000
    Rental Vacancy: x%
    Rental Yield: y%
    Background Information: These cities are typically located near major transport hubs, 
    employment centers, and educational institutions. 
    The following list highlights some of the top contenders for investment opportunities """,
    agent=property_researcher,
    output_file="research_task_output_internet.txt"
)
