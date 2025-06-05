from openai import OpenAI
import os
import ast
from agentpro.tools import Tool
from typing import Any, Dict

class MealPlannerTool(Tool):
    name: str = "Meal Planner Tool"
    description: str = (
        "Generates a detailed meal plan for any event based on event type, location, and schedule."
    )
    action_type: str = "generate_meal_plan"
    input_format: str = (
        "Dict with keys: 'event_type', 'location', and 'schedule'."
    )

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        event_type = input_data.get("event_type", "general event")
        location = input_data.get("location", "unknown location")
        schedule = input_data.get("schedule", [])

        prompt = f"""
You are an expert catering planner.

Create a culturally appropriate, structured meal plan for:

- Event Type: {event_type}
- Location: {location}
- Schedule: {schedule}

Return a Python dictionary with keys:
- 'breakfast': [...]
- 'lunch': [...]
- 'snacks': [...]
- 'dinner': [...]
- 'special_requests': "..."

Ensure output is valid Python.
IMPORTANT: Respond immediately with the final JSON object using only Final Answer: followed by the valid JSON.\n"
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You plan meals for global events."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content

        try:
            meal_plan = ast.literal_eval(content.strip())
            return {"meal_plan": meal_plan}
        except Exception as e:
            return {
                "error": "Parsing failed",
                "raw_output": content,
                "exception": str(e)
            }
