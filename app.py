import streamlit as st
from orchestrator import orchestrated_event_plan
from user_intent_agent import extract_user_intent  # adjust path if needed

st.set_page_config(page_title="AI Event Manager", page_icon="🎉")
st.title("🎉 AI Event Manager")
st.markdown("Plan entire events — venues, catering, hotels, weather — with a single query!")

user_query = st.text_area("📝 Describe your event", 
    placeholder="e.g. Plan a wedding in Islamabad on June 13 with 300 guests")

if st.button("🧠 Plan Event"):
    with st.spinner("Processing..."):
        try:
            user_intent = extract_user_intent(user_query)
            st.subheader("🎯 Extracted Intent")
            st.json(user_intent)

            plan = orchestrated_event_plan(user_intent)
            st.subheader("🧩 Event Plan Summary")
            for section, content in plan["summary"].items():
                st.markdown(f"### 🔹 {section.capitalize()}")
                st.json(content)
        except Exception as e:
            st.error(f"❌ Error: {e}")
