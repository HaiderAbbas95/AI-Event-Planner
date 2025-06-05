import sys
import os
import json
import re

# Add AgentPro to path
sys.path.insert(0, "/content/AgentPro")

from agentpro import create_model, ReactAgent

# ✅ Create GPT-4o model client
model = create_model(
    provider="openai",
    model_name="gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"]
)

agent = ReactAgent(model=model, tools=[])

# 📦 Extract structured list from LLM output
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

# 📅 Scheduler Agent logic
def scheduler_agent(user_intent):
    """
    Uses GPT-4o to generate a high-level multi-day schedule based on intent.
    """
    event_type = user_intent.get("event_type")
    event_date = user_intent.get("event_date") or "a typical day"
    guest_count = user_intent.get("guest_count", "unknown")

    if not event_type:
        raise ValueError("User intent must include an event_type.")

    prompt = (
        f"You are an expert event planner. Create a high-level multi-day schedule for a {event_type} "
        f"beginning on {event_date} with around {guest_count} guests. Include major activities from arrival to departure:\n"
        f"airport pickups, hotel check-in, meals, sessions, sightseeing in free slots, and checkout.\n"
        f"Return the result as a Python list of dictionaries in this format:\n\n"
        f"Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        f"[{{\"day\": \"Day 1 - Arrival\", \"activities\": [\"Hotel check-in\", \"Welcome dinner\"]}}, ...]"
        f"IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )

    print("🧠 Prompting GPT-4o for schedule...")
    response = agent.run(prompt).final_answer
    schedule = extract_json_from_response(response)
    return schedule

# 🔁 Run in standalone mode
if __name__ == "__main__":
    try:
        user_intent = extracted_intent  # Make sure this is defined globally
    except NameError:
        raise Exception("❌ 'extracted_intent' not defined. Run User Intent Agent first.")

    print("\n🎯 Extracted User Intent:")
    print(json.dumps(user_intent, indent=2))

    print("\n📅 Generating high-level schedule...")
    schedule = scheduler_agent(user_intent)

    print("\n🗓️ Multi-day Itinerary:")
    for day in schedule:
        print(f"\n📌 {day['day']}")
        for act in day["activities"]:
            print(f"   - {act}")
