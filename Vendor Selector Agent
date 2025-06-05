import os
import json
import requests
import ast
import re
from agentpro import ReactAgent, create_model
from agentpro.tools import QuickInternetTool

# ✅ Load keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure it's set in environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Make sure it's set in environment

# ✅ Create OpenAI model (GPT-4o or GPT-4)
model = create_model(
    provider="openai",
    model_name="gpt-4o",
    api_key=OPENAI_API_KEY
)

# ✅ Setup ReAct agent with tool
agent = ReactAgent(model=model, tools=[QuickInternetTool()])

# ✅ Utility to clean LLM list responses
def extract_json_list(response):
    cleaned = response.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[(.*?)\]", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(f"[{match.group(1)}]")
            except json.JSONDecodeError:
                pass
    raise ValueError(f"❌ Could not extract valid JSON list from LLM response:\n{cleaned}")

# ✅ LLM step to find vendor types
def get_required_vendor_types(event_type):
    prompt = (
        f"You are an expert event planner. What types of vendors are typically needed for a '{event_type}'? "
        "Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        "Return only a Python list like: [\"catering\", \"event lighting\", \"A/V equipment\"]"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )
    response = agent.run(prompt)
    return extract_json_list(response.final_answer)

# ✅ Google Places API
def search_vendors(location, vendor_type, limit=3):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{vendor_type} near {location}",
        "key": GOOGLE_API_KEY
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    vendors = []
    for result in results:
        place_id = result.get("place_id")
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,formatted_phone_number,website",
            "key": GOOGLE_API_KEY
        }
        detail_resp = requests.get(details_url, params=details_params).json()
        d = detail_resp.get("result", {})
        vendors.append({
            "name": d.get("name"),
            "type": vendor_type,
            "rating": d.get("rating", "N/A"),
            "address": d.get("formatted_address", "N/A"),
            "phone": d.get("formatted_phone_number", "N/A"),
            "website": d.get("website", "N/A")
        })

    return vendors

# ✅ Main agent
def vendors_agent(user_intent):
    event_type = user_intent.get("event_type")
    location = user_intent.get("location")

    if not event_type or not location:
        raise ValueError("User intent must include both event_type and location.")

    vendor_types = get_required_vendor_types(event_type)
    all_vendors = []

    for vtype in vendor_types:
        print(f"🔎 Searching vendors for: {vtype}")
        vendors = search_vendors(location, vtype)
        all_vendors.append({
            "vendor_type": vtype,
            "options": vendors
        })

    return all_vendors

# ✅ Run if main
if __name__ == "__main__":
   
    print("\n🎯 Extracted Intent:")
    print(json.dumps(extracted_intent, indent=2))

    print("\n🔧 Finding vendors...")
    vendor_results = vendors_agent(extracted_intent)

    print("\n🛍️ Recommended Vendors:")
    for group in vendor_results:
        print(f"\n🔹 Vendor Type: {group['vendor_type']}")
        for idx, v in enumerate(group["options"], start=1):
            print(f"  {idx}. {v['name']} ({v['rating']})")
            print(f"     📍 {v['address']}")
            print(f"     ☎️ {v['phone']}")
            print(f"     🌐 {v['website']}")
