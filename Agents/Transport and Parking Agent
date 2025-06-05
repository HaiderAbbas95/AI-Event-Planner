import os
import json
import ast
import re
import requests
from agentpro import ReactAgent, create_model

# ✅ Use OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "❌ Missing OPENAI_API_KEY in environment"

# ✅ Create model + ReAct agent with OpenAI GPT-4o
model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model)

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

def analyze_transport_needs(user_intent, venues, schedule):
    prompt = (
        "You are a logistics planner. Based on this event, return:\n"
        "- A list of transport vendor types required\n"
        "- A dictionary of estimated vehicle needs by type\n\n"
        "Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        "Return this as a Python dictionary with two keys: 'vendor_types' and 'vehicle_estimates'.\n"
        "Example:\n"
        "{\n"
        "  \"vendor_types\": [\"shuttle service\", \"bus rental\"],\n"
        "  \"vehicle_estimates\": {\"cars\": 3, \"shuttles\": 2, \"buses\": 1}\n"
        "}\n\n"
        f"user_intent = {json.dumps(user_intent, indent=2)}\n"
        f"venues = {json.dumps(venues[:2], indent=2)}\n"
        f"schedule = {json.dumps(schedule[:2], indent=2)}"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )

    response = agent.run(prompt)
    cleaned = extract_json_from_response(response.final_answer)

    try:
        if isinstance(cleaned, dict):
            data = cleaned
        elif isinstance(cleaned, str):
            try:
                data = ast.literal_eval(cleaned)
            except Exception:
                data = json.loads(cleaned.replace("'", '"'))
        else:
            raise Exception("LLM returned unparseable content")

        if isinstance(data, dict) and "vendor_types" in data and "vehicle_estimates" in data:
            return data
        else:
            raise ValueError("Unexpected LLM output structure:\n" + json.dumps(data, indent=2))

    except Exception as e:
        raise Exception(f"LLM response could not be parsed:\n{cleaned}\n\nError: {e}")

def search_vendors(location, vendor_type, limit=3):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{vendor_type} near {location}",
        "key": os.getenv("GOOGLE_API_KEY")
    }
    res = requests.get(url, params=params).json()
    results = res.get("results", [])[:limit]

    vendors = []
    for r in results:
        vendors.append({
            "name": r.get("name"),
            "type": vendor_type,
            "address": r.get("formatted_address"),
            "rating": r.get("rating", "N/A")
        })
    return vendors

def get_nearest_transport_hubs(location):
    airport = search_vendors(location, "international airport", limit=1)
    railway = search_vendors(location, "intercity railway station", limit=1)
    bus = search_vendors(location, "intercity bus terminal", limit=1)

    return {
        "nearest_airport": airport[0] if airport else {"name": "N/A", "address": "N/A"},
        "nearest_railway_station": railway[0] if railway else {"name": "N/A", "address": "N/A"},
        "nearest_bus_station": bus[0] if bus else {"name": "N/A", "address": "N/A"},
    }

def find_parking_near_venues(venues):
    parking_results = {}
    for v in venues:
        venue_name = v.get("name")
        venue_address = v.get("address") or v.get("formatted_address")
        if not venue_name or not venue_address:
            continue

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"parking near {venue_address}",
            "key": os.getenv("GOOGLE_API_KEY")
        }
        res = requests.get(url, params=params).json()
        results = res.get("results", [])[:3]

        parking_spots = [{
            "name": r.get("name"),
            "address": r.get("formatted_address"),
            "rating": r.get("rating", "N/A")
        } for r in results]

        parking_results[venue_name] = parking_spots
    return parking_results

def transport_parking_agent(user_intent, venue_data, schedule_data):
    location = user_intent.get("location")
    event_type = user_intent.get("event_type")
    if not location or not event_type:
        raise ValueError("Missing location or event_type.")

    all_venues = []
    for group in venue_data:
        all_venues.extend(group.get("options", []))

    transport_plan = analyze_transport_needs(user_intent, all_venues, schedule_data)
    vendor_types = transport_plan.get("vendor_types", [])
    vehicle_estimates = transport_plan.get("vehicle_estimates", {})

    vendor_recs = []
    for vtype in vendor_types:
        vendor_recs.append({
            "vendor_type": vtype,
            "options": search_vendors(location, vtype)
        })

    return {
        "transport_plan": {
            "vendor_types": vendor_types,
            "vehicle_estimates": vehicle_estimates
        },
        "vendor_recommendations": vendor_recs,
        "parking_near_venues": find_parking_near_venues(all_venues),
        "transport_hubs": get_nearest_transport_hubs(location)
    }

if __name__ == "__main__":
    user_intent = extracted_intent
    venue_data = venue_agent(user_intent)
    schedule_data = scheduler_agent(user_intent)
    transport_output = transport_parking_agent(user_intent, venue_data, schedule_data)

    print("\n🚗 Vehicle Estimates:")
    for k, v in transport_output["transport_plan"]["vehicle_estimates"].items():
        print(f"- {k.title()}: {v}")

    print("\n🛻 Transport Vendors:")
    for group in transport_output["vendor_recommendations"]:
        print(f"\n🔹 {group['vendor_type'].title()}")
        for v in group["options"]:
            print(f"  - {v['name']} ({v['rating']}) - {v['address']}")

    print("\n🅿️ Parking Near Venues:")
    for venue, lots in transport_output["parking_near_venues"].items():
        print(f"\n{venue}")
        for lot in lots:
            print(f"  - {lot['name']} ({lot['rating']}) - {lot['address']}")

    print("\n🚉 Nearest Transport Hubs:")
    hubs = transport_output.get("transport_hubs", {})
    print(f"🛫 Airport: {hubs.get('nearest_airport', {}).get('name', 'N/A')} - {hubs.get('nearest_airport', {}).get('address', 'N/A')}")
    print(f"🚆 Railway: {hubs.get('nearest_railway_station', {}).get('name', 'N/A')} - {hubs.get('nearest_railway_station', {}).get('address', 'N/A')}")
    print(f"🚌 Bus Station: {hubs.get('nearest_bus_station', {}).get('name', 'N/A')} - {hubs.get('nearest_bus_station', {}).get('address', 'N/A')}")
