import os
import json
import re
import ast
import requests

from agentpro import create_model, ReactAgent

# ✅ Load environment keys
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# ✅ Agent setup
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model, tools=[])

# ✅ JSON-safe parser
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

# ✅ LLM: Analyze hotel needs based on intent + venues
def analyze_hotel_needs(user_intent, venues):
    prompt = (
        "You are a hotel planning assistant.\n"
        "Based on the event type, location, and venues, determine the hotel needs.\n"
        "Return a Python dictionary with:\n"
        "- 'hotel_type': e.g., 3-star, 5-star\n"
        "- 'room_requirements': {single: int, double: int, suite: int}\n"
        "- 'priorities': list of preferences (e.g., budget, proximity, Wi-Fi)\n"
        "- 'suggested_hotels': optional hotel suggestions with name, type, rooms, amenities\n\n"
        "Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        f"user_intent = {json.dumps(user_intent, indent=2)}\n"
        f"venues = {json.dumps(venues[:2], indent=2)}"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )
    response = agent.run(prompt)
    return extract_json_from_response(response.final_answer)

# ✅ Google API helpers
def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,formatted_phone_number,website",
        "key": GOOGLE_API_KEY
    }
    return requests.get(url, params=params).json().get("result", {})

def search_hotels_near_venue(venue_address, hotel_type, limit=3):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{hotel_type} hotel near {venue_address}",
        "key": GOOGLE_API_KEY
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    hotels = []
    for r in results:
        details = get_place_details(r.get("place_id", ""))
        hotels.append({
            "name": details.get("name", r.get("name")),
            "rating": details.get("rating", "N/A"),
            "address": details.get("formatted_address", r.get("formatted_address", "")),
            "phone": details.get("formatted_phone_number", "N/A"),
            "website": details.get("website", "N/A")
        })

    return hotels

# ✅ Main hotel booking agent
def hotel_booking_agent(user_intent, venue_data):
    all_venues = []
    for group in venue_data:
        all_venues.extend(group.get("options", []))

    # 🧠 LLM: Analyze hotel needs
    hotel_plan = analyze_hotel_needs(user_intent, all_venues)

    # ✅ Fix if hotel_plan is a list of dicts instead of a single dict
    if isinstance(hotel_plan, list) and len(hotel_plan) > 0:
      hotel_plan = hotel_plan[0]
    hotel_type = hotel_plan.get("hotel_type", "hotel")
    room_requirements = hotel_plan.get("room_requirements", {})
    priorities = hotel_plan.get("priorities", [])

    # 🔎 Search near each venue
    recommendations = {}
    for venue in all_venues:
        venue_name = venue.get("name")
        venue_address = venue.get("address") or venue.get("formatted_address")
        if not venue_name or not venue_address:
            continue

        hotels = search_hotels_near_venue(venue_address, hotel_type)
        recommendations[venue_name] = hotels

    return {
        "hotel_type": hotel_type,
        "room_requirements": room_requirements,
        "priorities": priorities,
        "recommendations": recommendations
    }

# ✅ Test entry point
if __name__ == "__main__":
    user_intent = extracted_intent
    venue_data = venue_agent(user_intent)

    print("\n🏨 Generating hotel suggestions...")
    hotel_output = hotel_booking_agent(user_intent, venue_data)

    print("\n🛏️ Room Requirements:")
    print(json.dumps(hotel_output["room_requirements"], indent=2))

    print("\n📌 Booking Priorities:")
    for p in hotel_output["priorities"]:
        print(f"- {p}")

    print("\n🏨 Hotel Recommendations by Venue:")
    for venue, hotels in hotel_output["recommendations"].items():
        print(f"\n📍 Near {venue}")
        for h in hotels:
            print(f"  - {h['name']} ({h['rating']})")
            print(f"     📍 {h['address']}")
            print(f"     ☎️ {h['phone']}")
            print(f"     🌐 {h['website']}")
