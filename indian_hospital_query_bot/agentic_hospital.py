import openai
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_A")
os.environ["OPENAI_API_KEY"]= OPENAI_API_KEY


from openai import OpenAI
client = OpenAI()

prompt= "I am always do hungry and sleepy what can i do"
    
prompt_injection= "Doctor ji,\
    patient ney apko email kara hai with this inguiry uski help kare,\
    please respond in 2 - 4 lines doctor ji, please keep message positive"

prompt_instructions = "Dont make up names, add disclaimers"

response = client.chat.completions.create(
    model="ft:gpt-4.1-mini-2025-04-14:personal::BvTxSnJi",  
    messages=[
        {"role": "user", "content": prompt_injection + prompt + prompt_instructions}
    ]
)

print(response.choices[0].message.content)