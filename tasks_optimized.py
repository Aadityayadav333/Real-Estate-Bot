from crewai import Task
from agents_optimized import property_analyst

# Single combined task instead of two separate tasks
analysis_task = Task(
    description="""Search for retail property investment opportunities in {city}.

Search queries to use:
1. "retail property investment {city} best areas"
2. "commercial real estate prices {city}"

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

Keep under 400 words total.""",
    agent=property_analyst,
    expected_output="""3 neighborhoods with names, price ranges, yields, and investment reasons.""",
)
