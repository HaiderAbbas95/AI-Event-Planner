import os
import json
import requests
from agentpro import create_model, ReactAgent
from agentpro.tools import QuickInternetTool

# ✅ Load API keys from environment
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# ✅ Setup model + agent
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model, tools=[QuickInternetTool()])  # tool not used yet, but available

# ✅ JSON extraction (robust for LLM output)
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

# ✅ Get venue types for given event
def get_suitable_venue_types(event_type):
    prompt = (
        f"You are an expert event planner.\n"
        f"Suggest the 3 most suitable types of venues for a '{event_type}' event.\n"
        f"Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        f"Return only a valid JSON list like: [\"banquet hall\", \"outdoor garden\", \"conference center\"]"
        f"IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )
    response = agent.run(prompt)
    return extract_json_list(response.final_answer)

# ✅ Search Google Places for venue info
def search_venues(location, venue_type, limit=3):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{venue_type} in {location}",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(search_url, params=params)
    results = response.json().get("results", [])[:limit]

    venues = []
    for result in results:
        place_id = result.get("place_id")
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,formatted_phone_number,website",
            "key": GOOGLE_API_KEY
        }
        detail_resp = requests.get(details_url, params=details_params).json()
        detail = detail_resp.get("result", {})

        venues.append({
            "name": detail.get("name", "N/A"),
            "rating": detail.get("rating", "N/A"),
            "address": detail.get("formatted_address", "N/A"),
            "phone": detail.get("formatted_phone_number", "N/A"),
            "website": detail.get("website", "N/A")
        })

    return venues

# ✅ Main venue agent logic
def venue_agent(extracted_intent):
    event_type = extracted_intent.get("event_type")
    location = extracted_intent.get("location")

    if not event_type or not location:
        raise ValueError("❌ User intent must include both 'event_type' and 'location'.")

    print(f"\n🧠 Determining suitable venue types for: {event_type}")
    venue_types = get_suitable_venue_types(event_type)

    all_venues = []
    for vtype in venue_types:
        print(f"🔎 Searching: {vtype} in {location}")
        venues = search_venues(location, vtype)
        all_venues.append({
            "venue_type": vtype,
            "options": venues
        })

    return all_venues

# ✅ Run standalone
if __name__ == "__main__":
    print("\n🎯 Extracted User Intent:")
    print(json.dumps(extracted_intent, indent=2))

    venue_results = venue_agent(extracted_intent)

    print("\n📍 Recommended Venues:")
    for group in venue_results:
        print(f"\n🔹 Venue Type: {group['venue_type']}")
        for i, v in enumerate(group["options"], start=1):
            print(f"  {i}. {v['name']}")
            print(f"     ⭐ Rating: {v.get('rating', 'N/A')}")
            print(f"     📍 Address: {v.get('address', 'N/A')}")
            print(f"     ☎️ Phone: {v.get('phone', 'N/A')}")
            print(f"     🌐 Website: {v.get('website', 'N/A')}\n")
