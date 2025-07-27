import openai
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import graph1
from graph1 import HospitalAgent

# Access environment variables
FUSION_MODEL_OAI=os.getenv("FUSION_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_A")
os.environ["OPENAI_API_KEY"]= OPENAI_API_KEY
from openai import OpenAI
client = OpenAI()


while True:
    Hospital_Chat =  HospitalAgent()
    query= input("Add your question:")
    answer= Hospital_Chat.run(query)
    print("MEDICAL response: ", answer["medical_answer"])
    print("\n\n")
    
    prompt_injection= "Doctor ji,\
    patient ney apko email kara hai with this inguiry uski help kare,\
    please respond in 2 - 4 lines doctor ji, please keep message positive"
    prompt_instructions = "Dont make up names, add disclaimers"
    
    response_doc = client.chat.completions.create(
    model=FUSION_MODEL_OAI,  
    messages=[
        {"role": "user", "content": prompt_injection +  answer["final_response"] + prompt_instructions}
    ]
    )
    print("EMAIL FROM THE DOCTOR IS :")
    print(response_doc.choices[0].message.content+ "\n\n")
    print("________________________")