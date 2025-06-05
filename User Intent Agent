import sys
import os
import re
import json 
import ast
import dateparser

# Add AgentPro to system path
sys.path.insert(0, "/content/AgentPro")

# ✅ AgentPro imports
from agentpro import ReactAgent, create_model
from agentpro.tools import UserInputTool  # optional

# ✅ Create model wrapper (this solves the .chat_completion error)
model = create_model(
    provider="openai",
    model_name="gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"]
)

agent = ReactAgent(model=model, tools=[])

# 🧼 LLM response parser
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

# 🚀 Main user intent extraction
def extract_user_intent():
    user_query = input("👤 Please describe the event you want to plan (type, location, guests, etc.):\n> ")

    prompt = (
      "You are an event planning assistant.\n"
      "Extract structured event info from the user query below.\n"
      "Return a **Python dictionary only**, no explanations or formatting.\n\n"
      "Required dictionary keys:\n"
      "- 'event_type': string\n"
      "- 'location': string\n"
      "- 'event_date': string (YYYY-MM-DD)\n"
      "- 'guest_count': integer\n"
      "- 'preferences': dictionary (include keys like 'stay_dates', 'guest_origins', etc.)\n"
      "- 'event_theme': string (optional)\n"
      "- 'meal_count': integer (optional)\n"
      "- 'transport_needs': string (optional)\n"
      "- 'sightseeing': boolean (optional)\n\n"
      "Missing values must be set to null.\n\n"
      "Output should be in pure JSON form and nothing else should be included which is not in JSON format"
      f"User input: {user_query}"
      "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
)


    print("🔁 Querying GPT-4o via ReAct agent...")
    response = agent.run(prompt)
    raw_output = response.final_answer
    print("🧠 LLM RAW OUTPUT:\n", raw_output)

    intent_data = extract_json_from_response(raw_output)

    if intent_data.get("event_date"):
        parsed_date = dateparser.parse(intent_data["event_date"])
        intent_data["event_date"] = parsed_date.strftime("%Y-%m-%d") if parsed_date else None

    print("\n✅ Extracted User Intent:")
    print(json.dumps(intent_data, indent=2))
    return intent_data

# Run the extraction
extracted_intent = extract_user_intent()
