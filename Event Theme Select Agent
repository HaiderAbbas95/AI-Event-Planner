import os
import json
import ast
import re
import requests
from agentpro import ReactAgent, create_model

# ✅ Use OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "❌ Missing OPENAI_API_KEY in environment"

# ✅ Create ReAct Agent using GPT-4o
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model, tools=[])


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



def get_vendor_details(query, location, limit=3):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} near {location}",
        "key": os.getenv("GOOGLE_API_KEY")
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    vendors = []
    for r in results:
        place_id = r.get("place_id")
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,formatted_phone_number,website",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        details = requests.get(details_url, params=details_params).json().get("result", {})
        vendors.append({
            "name": details.get("name"),
            "address": details.get("formatted_address"),
            "phone": details.get("formatted_phone_number", "N/A"),
            "website": details.get("website", "N/A"),
            "rating": details.get("rating", "N/A"),
            "type": query
        })
    return vendors

def analyze_theme(user_intent):
    prompt = (
        "You are a creative event theme planner. Based on the event intent below, suggest a detailed event theme plan.\n"
        "Include:\n"
        "1. A creative theme name and style\n"
        "2. A list of decor elements needed (like penaflex, stage, lighting, florals)\n"
        "3. Any custom branding or stage setup suggestions\n"
        "Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        "Return as a JSON dictionary with keys: theme_name, style_description, required_elements, branding_notes.\n"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
        f"user_intent = {json.dumps(user_intent, indent=2)}"
    )
    response = agent.run(prompt)
    return extract_json_from_response(response.final_answer)

def theme_agent(user_intent):
    location = user_intent.get("location")
    if not location:
        raise ValueError("Location not found in user intent")

    theme_plan = analyze_theme(user_intent)

    required_elements = theme_plan.get("required_elements", [])
    if isinstance(required_elements, dict):
        required_elements = [item.get("item") for item in required_elements.get("decor", []) if item.get("item")]

    vendor_list = []
    for item in required_elements:
        vendor_list.extend(get_vendor_details(item, location))

    return {
        "recommended": {
            "theme_name": theme_plan.get("theme_name"),
            "style_description": theme_plan.get("style_description"),
            "branding_notes": theme_plan.get("branding_notes", ""),
            "required_elements": required_elements
        },
        "alternates": [],
        "vendors": vendor_list
    }

if __name__ == "__main__":
    user_intent = extracted_intent
    print("\n🎨 Generating Event Theme Plan...")
    theme_output = theme_agent(user_intent)

    recommended = theme_output["recommended"]

    print(f"\n🎭 Theme Name: {recommended['theme_name']}")
    print(f"🕋️ Description: {recommended['style_description']}")
    print(f"🧾 Branding Notes: {recommended['branding_notes']}")
    print(f"\n🛠️ Required Decor Elements:")
    for e in recommended['required_elements']:
        print(f"- {e}")

    print(f"\n🏢 Vendor Recommendations:")
    for v in theme_output['vendors']:
        print(f"\n🔹 {v['type'].title()} Vendor")
        print(f"  Name: {v['name']}")
        print(f"  📍 Address: {v['address']}")
        print(f"  ☎️ Phone: {v['phone']}")
        print(f"  🌐 Website: {v['website']}")
        print(f"  ⭐ Rating: {v['rating']}")
