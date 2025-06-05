!git clone https://github.com/traversaal-ai/AgentPro.git
# Install any needed libraries (some may already be installed)
!pip install openai requests scipy
!pip install dateparser
# Import libraries
import openai
import json
import requests
import numpy as np
from scipy.optimize import linprog
import os
from google.colab import userdata
from datetime import datetime, time
import dateparser
from datetime import datetime, timezone, timedelta
from google.colab import userdata
OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
print("Google API key loaded:", bool(GOOGLE_API_KEY))
print("OPEN AI API key loaded:", bool(OPENAI_API_KEY))
%cd AgentPro
!pip install -e .
from google.colab import userdata
import os

# Set keys from secrets
os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
os.environ["GOOGLE_API_KEY"] = userdata.get("GOOGLE_API_KEY")

print("✅ API keys successfully loaded into environment.")
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a catering expert."},
        {"role": "user", "content": "Create a meal plan for a tech conference in Dubai."}
    ]
)

print(response.choices[0].message.content)
