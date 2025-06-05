import sys
import os
import json
import requests

# AgentPro setup
sys.path.insert(0, "/content/AgentPro")
from agentpro import ReactAgent, create_model
from agentpro.tools import MealPlannerTool

# Load keys from environment
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Create model and agent
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
meal_tool = MealPlannerTool()
agent = ReactAgent(model=model, tools=[meal_tool])
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

# 🎯 Main catering agent logic
def catering_agent(user_intent, schedule):
    location = user_intent.get("location", "")
    if not location:
        raise ValueError("❌ Location missing in user intent.")

    # Run tool via ReAct agent
    llm_input = {
        "event_type": user_intent.get("event_type", "event"),
        "location": location,
        "schedule": schedule
    }

    print("🧠 Calling MealPlannerTool via ReAct agent...")
    response = agent.run(
        f"Use the meal planner tool to suggest an appropriate structured meal plan for the event in {location} based on the schedule."
        f" Use the schedule and intent below:\n\n{json.dumps(llm_input, indent=2)}"
        f"IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )

    if isinstance(response.final_answer, dict):
      meal_plan = response.final_answer.get("meal_plan", response.final_answer)
    else:
    # fallback for formatted string meal plan
      meal_plan = response.final_answer


    # 🔍 Use Google Places to find caterers
    caterer_recommendations = {}
    for meal in ["breakfast", "lunch", "dinner"]:  # Simplified; can use meal_plan keys
        vendors = search_caterers(location, meal)
        caterer_recommendations[meal] = vendors

    return {
        "catering_plan": meal_plan,
        "caterer_recommendations": caterer_recommendations
    }

# 📍 Google Places search
def search_caterers(location, meal_type, limit=3):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{meal_type} catering near {location}",
        "key": GOOGLE_API_KEY
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    caterers = []
    for r in results:
        place_id = r.get("place_id")
        detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
        detail_params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,formatted_phone_number,website",
            "key": GOOGLE_API_KEY
        }
        d = requests.get(detail_url, params=detail_params).json().get("result", {})
        caterers.append({
            "name": d.get("name"),
            "rating": d.get("rating", "N/A"),
            "address": d.get("formatted_address"),
            "phone": d.get("formatted_phone_number", "N/A"),
            "website": d.get("website", "N/A")
        })

    return caterers

# 🧪 Example usage
if __name__ == "__main__":
    user_intent = extracted_intent
    schedule = scheduler_agent(user_intent)

    print("\n🍽️ Running Catering Agent...")
    catering_result = catering_agent(user_intent, schedule)

    print("\n🧾 Catering Plan:")
    print(json.dumps(catering_result["catering_plan"], indent=2))

    print("\n👨‍🍳 Caterer Recommendations:")
    for meal, vendors in catering_result["caterer_recommendations"].items():
        print(f"\n🍴 {meal.title()}:")
        for v in vendors:
            print(f"  - {v['name']} ({v['rating']})")
            print(f"    📍 {v['address']}")
            print(f"    ☎️ {v['phone']}")
            print(f"    🌐 {v['website']}")
