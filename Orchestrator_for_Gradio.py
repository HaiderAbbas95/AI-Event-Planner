import os
import json
import openai

# Set your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")


# 🧠 Call GPT-4o to summarize each section
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🧠 GPT prompt call using new SDK
def ask_gpt(prompt):
    print("🧠 Calling OpenAI...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert event planner assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 📦 Extract only JSON from LLM output
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



# 🎯 Intent Extraction
def extract_user_intent(query):
    prompt = f"""
Extract the following details from the user message:
- event_type
- location
- event_date
- number_of_guests
- preferences (optional)

Respond with `Final Answer:` followed by a JSON object only.

Message: {query}
"""
    response = ask_gpt(prompt)
    return extract_json_from_response(response)


# 🔄 Orchestrator Agent
def orchestrated_event_plan(user_intent):
    print("🚀 Running Full Event Orchestrator...")

    # --- Step 1: Agent Calls ---
    venue_results = venue_agent(user_intent)
    vendor_results = vendors_agent(user_intent)
    schedule = scheduler_agent(user_intent)
    transport = transport_parking_agent(user_intent, venue_results, schedule)
    hotels = hotel_booking_agent(user_intent, venue_results)
    sightseeing = sightseeing_agent(user_intent, schedule)
    catering = catering_agent(user_intent, schedule)
    theme = theme_agent(user_intent)
    weather = weather_predictor_agent(user_intent, schedule)

    # --- Step 2: LLM Summaries ---
    def summarize(section_name, data):
        prompt = (
            f"You are summarizing the '{section_name}' section from an event planning agent.\n"
            f"Here is the agent output:\n\n{json.dumps(data, indent=2)}\n\n"
            "Summarize the best 2–3 items. Use bullets or clean formatting.\n"
            "Respond with only JSON — start with Final Answer: and no explanation."
        )
        response = ask_gpt(prompt)
        return extract_json_from_response(response)

    summary = {
        "venues": summarize("venues", venue_results),
        "vendors": summarize("vendors", vendor_results),
        "schedule": summarize("schedule", schedule),
        "transportation": summarize("transportation", transport),
        "hotels": summarize("hotels", hotels),
        "sightseeing": summarize("sightseeing", sightseeing),
        "catering": summarize("catering", catering),
        "theme": summarize("theme", theme),
        "weather_forecast": summarize("weather_forecast", weather)
    }

    return {
        "intent": user_intent,
        "summary": summary,
        "details": {
            "venues": venue_results,
            "vendors": vendor_results,
            "schedule": schedule,
            "transportation": transport,
            "hotels": hotels,
            "sightseeing": sightseeing,
            "catering": catering,
            "theme": theme,
            "weather_forecast": weather
        }
    }
if __name__ == "__main__":
    user_query = input("📝 Describe your event: ")

    try:
        intent = extract_user_intent(user_query)
        print("\n🎯 Extracted Intent:")
        print(json.dumps(intent, indent=2))

        plan = orchestrated_event_plan(intent)
        print("\n✅ Final Event Plan:")
        print(json.dumps(plan["summary"], indent=2))

    except Exception as e:
        print("❌ Error during event planning:", e)
