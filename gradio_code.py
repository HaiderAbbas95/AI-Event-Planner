!pip install gradio
!python gradio_app.py
import gradio as gr

# Global state
user_intent_state = {}

# Unified extract + cache
def extract_intent_interface(query):
    try:
        intent = extract_user_intent(query)
        user_intent_state["intent"] = intent
        return f"🎯 Intent extracted:\n```json\n{json.dumps(intent, indent=2)}\n```"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Agent output wrappers
def run_agent(agent_func, label):
    try:
        intent = user_intent_state.get("intent")
        if not intent:
            return "⚠️ Please extract intent first by entering a query."

        if "schedule" in agent_func.__name__:
            result = agent_func(intent)
        elif "weather" in agent_func.__name__:
            schedule = scheduler_agent(intent)
            result = agent_func(intent, schedule)
        elif "transport" in agent_func.__name__:
            schedule = scheduler_agent(intent)
            venues = venue_agent(intent)
            result = agent_func(intent, venues, schedule)
        elif "hotel" in agent_func.__name__:
            venues = venue_agent(intent)
            result = agent_func(intent, venues)
        elif "sightseeing" in agent_func.__name__ or "catering" in agent_func.__name__:
            schedule = scheduler_agent(intent)
            result = agent_func(intent, schedule)
        else:
            result = agent_func(intent)

        return f"### ✅ {label} Output\n```json\n{json.dumps(result, indent=2)}\n```"
    except Exception as e:
        return f"❌ {label} failed: {str(e)}"

# Main plan button
def run_orchestrator(query):
    try:
        intent = extract_user_intent(query)
        plan = orchestrated_event_plan(intent)

        display = f"### 🎯 Extracted Intent\n```json\n{json.dumps(intent, indent=2)}\n```\n"
        display += "### 🧩 Event Summary\n"
        for k, v in plan["summary"].items():
            display += f"#### {k.title()}\n```json\n{json.dumps(v, indent=2)}\n```\n"
        return display
    except Exception as e:
        return f"❌ Error during full planning: {e}"

# Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎉 AI Event Planner – Agent Explorer")
    query = gr.Textbox(label="📝 Describe your event")
    with gr.Row():
        intent_btn = gr.Button("🎯 Extract Intent")
        full_plan_btn = gr.Button("🧠 Generate Full Plan")
    intent_out = gr.Markdown()

    intent_btn.click(fn=extract_intent_interface, inputs=query, outputs=intent_out)
    full_plan_btn.click(fn=run_orchestrator, inputs=query, outputs=intent_out)

    gr.Markdown("## 🧩 Individual Agent Outputs")

    with gr.Row():
        venue_btn = gr.Button("📍 Venues")
        vendor_btn = gr.Button("🛠️ Vendors")
        schedule_btn = gr.Button("📅 Schedule")
        catering_btn = gr.Button("🍽️ Catering")
    with gr.Row():
        transport_btn = gr.Button("🚌 Transport")
        hotel_btn = gr.Button("🏨 Hotels")
        sightseeing_btn = gr.Button("🧭 Sightseeing")
        weather_btn = gr.Button("🌤️ Weather")
        theme_btn = gr.Button("🎨 Theme")

    agent_output = gr.Markdown()

    venue_btn.click(fn=lambda: run_agent(venue_agent, "Venues"), outputs=agent_output)
    vendor_btn.click(fn=lambda: run_agent(vendors_agent, "Vendors"), outputs=agent_output)
    schedule_btn.click(fn=lambda: run_agent(scheduler_agent, "Schedule"), outputs=agent_output)
    catering_btn.click(fn=lambda: run_agent(catering_agent, "Catering"), outputs=agent_output)
    transport_btn.click(fn=lambda: run_agent(transport_parking_agent, "Transport"), outputs=agent_output)
    hotel_btn.click(fn=lambda: run_agent(hotel_booking_agent, "Hotels"), outputs=agent_output)
    sightseeing_btn.click(fn=lambda: run_agent(sightseeing_agent, "Sightseeing"), outputs=agent_output)
    weather_btn.click(fn=lambda: run_agent(weather_predictor_agent, "Weather"), outputs=agent_output)
    theme_btn.click(fn=lambda: run_agent(theme_agent, "Theme"), outputs=agent_output)

app.launch(share=True)
