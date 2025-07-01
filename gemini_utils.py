import streamlit as st
import google.generativeai as genai


api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)    

def get_budget_advice(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text





