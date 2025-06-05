import sys
import json
from agentpro import ReactAgent, create_model
import os
#from user_intent_agent import extract_user_intent

# ✅ OpenAI model setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "❌ Missing OPENAI_API_KEY in environment"

model = create_model(provider="openai", model_name="gpt-4o", api_key=OPENAI_API_KEY)
agent = ReactAgent(model=model, tools=[])

import json
import ast
def summarize_output(section_name, data):
    prompt = (
        f"You are a summarizer for an event planner agent.\n"
        f"Please summarize the key information from the '{section_name}' section in bullet points, focusing on top recommended options only.\n\n"
        f"{section_name} data:\n{json.dumps(data, indent=2)}\n\n"
        "IMPORTANT: Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. "
        "Do NOT output thoughts, actions, or any reasoning."
    )

    print(f"\n📦 Summarizing section: {section_name}")
    response = agent.run(prompt)

    if not hasattr(response, "final_answer") or not response.final_answer.strip().startswith("{"):
        raise ValueError(f"❌ LLM did not return usable JSON. Raw output:\n{response.final_answer}")
    
    return extract_json_from_response(response.final_answer)

def summarize_output(section_name, data):
    prompt = (
        f"You are a summarizer for an event planner agent.\n"
        f"Return only a valid JSON object with no code block markers, no explanation, no markdown, no labels — just the raw JSON."
        f"Please summarize the key information from the '{section_name}' section in bullet points, focusing on top recommended options only.\n\n"
        f"{section_name} data:\n{json.dumps(data, indent=2)}"
        "IMPORTANT: In each sub agent, Respond immediately with the final JSON object using only `Final Answer:` followed by the valid JSON. Do NOT output thoughts, actions, or any reasoning."
    )
    return agent.run(prompt).final_answer

def orchestrated_event_plan(user_intent):
    print("\n🚀 Launching Orchestrator Agent...")

    # 1. Extract User Intent
    #from your_user_intent_module import extract_user_intent  # adjust import if needed
    #user_intent = extract_user_intent(user_query)

    print("\n🎯 User Intent:")
    print(json.dumps(user_intent, indent=2))

    # 2. Venue Options
    venue_results = venue_agent(user_intent)
    venue_summary = summarize_output("Venues", venue_results)

    # 3. Vendor Recommendations
    vendor_results = vendors_agent(user_intent)
    vendor_summary = summarize_output("Vendors", vendor_results)

    # 4. Event Schedule
    schedule = scheduler_agent(user_intent)

    # 5. Transport & Parking
    transport_output = transport_parking_agent(user_intent, venue_results, schedule)
    transport_summary = summarize_output("Transportation", transport_output)

    # 6. Hotel Options
    hotel_output = hotel_booking_agent(user_intent, venue_results)
    hotel_summary = summarize_output("Hotels", hotel_output)

    # 7. Sightseeing Plan
    sightseeing = sightseeing_agent(user_intent, schedule)
    sightseeing_summary = summarize_output("Sightseeing", sightseeing)

    # 8. Catering Options
    catering_result = catering_agent(user_intent, schedule)
    catering_summary = summarize_output("Catering", catering_result)

    # 9. Theme Plan
    theme_output = theme_agent(user_intent)
    theme_summary = summarize_output("Theme", theme_output)

    # 10. Weather Forecast
    forecast = weather_predictor_agent(user_intent, schedule)

    # 🧠 Final Output Structure
    event_plan = {
        "intent": user_intent,
        "summary": {
            "venues": venue_summary,
            "vendors": vendor_summary,
            "transportation": transport_summary,
            "hotels": hotel_summary,
            "sightseeing": sightseeing_summary,
            "catering": catering_summary,
            "theme": theme_summary,
        },
        "details": {
            "venues": venue_results,
            "vendors": vendor_results,
            "schedule": schedule,
            "transportation": transport_output,
            "hotels": hotel_output,
            "sightseeing": sightseeing,
            "catering": catering_result,
            "theme": theme_output,
            "weather_forecast": forecast,
        }
    }

    print("\n✅ Event Planning Complete!")
    return event_plan

# ✅ Run it
if __name__ == "__main__":
    extracted_intent = extract_user_intent()
    user_query = extracted_intent
    plan = orchestrated_event_plan(extracted_intent)
    
    print("\n📋 Summary Output:")
    print(json.dumps(plan["summary"], indent=2))
