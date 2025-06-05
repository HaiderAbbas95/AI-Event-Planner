import os
import json
import ast
import re
import requests
from agentpro import ReactAgent, create_model

# ✅ Use OpenAI API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "❌ Missing OPENAI_API_KEY in environment"

# ✅ Create ReAct Agent using GPT-4o
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model, tools=[])

import re
import json

def extract_json_from_response(response):
    cleaned = response.strip()
    cleaned = re.sub(r"```(?:json|python)?", "", cleaned)
    cleaned = re.sub(r"[^\x00-\x7F]+", "", cleaned).strip()
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    raise ValueError(f"❌ Could not extract valid JSON from LLM response:\n{cleaned}")

def analyze_sightseeing_need(user_intent, schedule):
    if isinstance(schedule, dict):
        schedule = list(schedule.values())
    elif not isinstance(schedule, list):
        raise Exception("❌ Schedule must be a list or a dictionary of days.")

    sample_schedule = []
    for entry in schedule[:2]:
        if isinstance(entry, dict) and 'day' in entry and 'activities' in entry:
            activity = entry['activities'][0] if isinstance(entry['activities'], list) else str(entry['activities'])
            sample_schedule.append(f"{entry['day']}: {activity}")
    schedule_snippet = "\n".join(sample_schedule)

    prompt = (
        "You are a cultural planner helping design event schedules.\n"
        "Given the event type and a brief schedule summary, recommend whether sightseeing could be meaningfully integrated.\n"
        "If so, suggest the type and ideal time.\n\n"
        "Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        "Return ONLY a Python dictionary with the following keys:\n"
        "- 'is_required' (true/false)\n"
        "- 'sightseeing_type' (e.g. cultural, shopping, historical)\n"
        "- 'integration_notes' (e.g. best added on Day 2 afternoon)\n\n"
        "Do NOT return anything else. No text. No schedule. No explanation. and no emojis\n"
        "Example:\n"
        "{\n"
        "  \"is_required\": true,\n"
        "  \"sightseeing_type\": \"Cultural\",\n"
        "  \"integration_notes\": \"Schedule it on Day 2 afternoon.\"\n"
        "}\n\n"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
        f"Event type: {user_intent.get('event_type')}\n"
        f"Schedule summary:\n{schedule_snippet}"
    )

    response = agent.run(prompt)
    return extract_json_from_response(response.final_answer)

def get_sightseeing_places(location, theme="cultural", limit=5):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{theme} attractions near {location}",
        "key": os.getenv("GOOGLE_API_KEY")
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    return [{
        "name": r.get("name"),
        "rating": r.get("rating", "N/A"),
        "address": r.get("formatted_address"),
        "type": theme,
        "description": r.get("types", [])
    } for r in results]

def sightseeing_agent(user_intent, schedule_data):
    location = user_intent.get("location")
    if not location:
        raise ValueError("Location not specified in user intent.")

    analysis = analyze_sightseeing_need(user_intent, schedule_data)

    if not analysis.get("is_required", False):
        return {
            "is_required": False,
            "reason": analysis.get("reason", "LLM suggested sightseeing is not appropriate.")
        }

    theme = analysis.get("sightseeing_type", "cultural")
    places = get_sightseeing_places(location, theme)

    return {
        "is_required": True,
        "sightseeing_type": theme,
        "integration_notes": analysis.get("integration_notes", ""),
        "suggested_places": places
    }

if __name__ == "__main__":
    user_intent = extracted_intent
    schedule_data = scheduler_agent(user_intent)
    sightseeing = sightseeing_agent(user_intent, schedule_data)

    if not sightseeing["is_required"]:
        print("❌ Sightseeing not included:")
        print("Reason:", sightseeing.get("reason"))
    else:
        print("\n✅ Sightseeing Included!")
        print("Type:", sightseeing["sightseeing_type"])
        print("When:", sightseeing["integration_notes"])
        print("\n📍 Suggested Places:")
        for s in sightseeing["suggested_places"]:
            print(f"- {s['name']} ({s['rating']}) — {s['address']}")
