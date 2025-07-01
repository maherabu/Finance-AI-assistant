import os
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
genai.configure(api_key=api_key)

def get_budget_advice(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text





