import streamlit as st
import uuid
import matplotlib.pyplot as plt
import pandas as pd

from gemini_utils import get_budget_advice

st.set_page_config(page_title="Finance Assistant 💰", layout="centered")

st.title("💸 Financial Assistant")
st.write("Upload a CSV or manually enter your income and expenses to receive financial advice.")

uploaded_file = st.file_uploader("📁 Upload your CSV file for Income & Expenses!", type="csv")

income = 0
expenses_dict = {}
used_csv = False

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Here's your uploaded data:")
    st.dataframe(df, use_container_width=True)

    if {"Type", "Category", "Amount"}.issubset(df.columns):
        income = df[df["Type"].str.lower() == "income"]["Amount"].sum()
        expense_df = df[df["Type"].str.lower() == "expense"]
        expenses_dict = expense_df.groupby("Category")["Amount"].sum().to_dict()
        st.success("✅ CSV successfully parsed.")
        st.write(f"💵 **Total Income:** ${income}")
        st.write("💸 **Expenses by Category:**")
        st.write(expenses_dict)
        used_csv = True
    else:
        st.error("Please make sure your CSV has 'Type', 'Category', and 'Amount' columns.")

if not used_csv:
    income = st.number_input("Monthly Income", min_value=0)

    common_categories = [
        "Rent", "Food", "Transportation", "Utilities", "Subscriptions", "Healthcare",
        "Education", "Entertainment", "Savings", "Debt", "Other"
    ]

    if "expenses" not in st.session_state:
        st.session_state.expenses = [{
            "id": str(uuid.uuid4()),
            "category": "Other",
            "custom": "",
            "amount": 0.0
        }]

    if st.button("➕ Add Expense"):
        st.session_state.expenses.append({
            "id": str(uuid.uuid4()),
            "category": "Other",
            "custom": "",
            "amount": 0.0
        })

    st.write("### Your Expenses:")

    for i, expense in enumerate(st.session_state.expenses):
        uid = expense["id"]
        cols = st.columns([3, 2, 1])

        selected = cols[0].selectbox(
            f"Category {i+1}",
            options=common_categories,
            index=common_categories.index(expense["category"]) if expense["category"] in common_categories else len(common_categories) - 1,
            key=f"select_{uid}"
        )
        st.session_state.expenses[i]["category"] = selected

        if selected == "Other":
            custom = cols[0].text_input(
                f"Custom Category {i+1}",
                value=expense.get("custom", ""),
                key=f"custom_{uid}"
            )
            st.session_state.expenses[i]["custom"] = custom
        else:
            st.session_state.expenses[i]["custom"] = ""

        st.session_state.expenses[i]["amount"] = cols[1].number_input(
            f"Amount {i+1}",
            min_value=0.0,
            value=expense["amount"],
            key=f"amount_{uid}"
        )

        if len(st.session_state.expenses) > 1:
            if cols[2].button("❌", key=f"remove_{uid}"):
                st.session_state.expenses.pop(i)
                st.experimental_rerun()

    expenses_dict = {
        (e['custom'] if e['category'] == 'Other' else e['category']): e['amount']
        for e in st.session_state.expenses if e['amount'] > 0
    }

if expenses_dict:
    st.write("### 📊 Expense Breakdown")
    fig, ax = plt.subplots()
    ax.pie(expenses_dict.values(), labels=expenses_dict.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

st.write("## 🧠 Financial Behavior Survey")

goal = st.selectbox("What is your main financial goal right now?", ["Save money", "Pay off debt", "Invest", "Budget better", "Other"])
goal_custom = st.text_input("Please describe your goal:") if goal == "Other" else ""
savings_goal = st.text_input("Do you have a specific savings goal? (e.g., $5000 in 6 months)")
timeline = st.radio("How soon do you want to achieve your goal?", ["< 3 months", "3–6 months", "6–12 months", "> 1 year"])
track_spending = st.radio("Do you track your spending regularly?", ["Yes", "No", "Sometimes"])
overspend = st.selectbox("Which category do you tend to overspend in?", ["Food", "Entertainment", "Online Shopping", "Subscriptions", "Other"])
overspend_custom = st.text_input("Enter your custom category:") if overspend == "Other" else ""
impulse = st.radio("How often do you impulse buy?", ["Frequently", "Occasionally", "Rarely", "Never"])
income_stability = st.radio("How stable is your monthly income?", ["Fixed", "Somewhat variable", "Highly variable"])
savings_percent = st.radio("What percentage of your income do you save monthly?", ["0–10%", "10–20%", "20–30%", "More than 30%", "I don’t save currently"])
emergency_fund = st.radio("Do you have an emergency fund?", ["Yes", "No", "I’m working on it"])
confidence = st.radio("How confident are you in managing your finances?", ["Very confident", "Somewhat confident", "Not confident"])
topics_to_learn = st.multiselect("What financial topics would you like to learn more about?", ["Budgeting", "Saving", "Investing", "Managing debt", "Retirement planning"])
wants_tips = st.radio("Would you like the app to provide educational tips based on your answers?", ["Yes", "No"])

formatted_expenses = ", ".join([f"{k} {v}" for k, v in expenses_dict.items()])

survey_summary = f"""
My goal is: {goal_custom or goal}.
I want to achieve this goal in: {timeline}.
I {'do' if track_spending == 'Yes' else 'do not' if track_spending == 'No' else 'sometimes'} track my spending.
I tend to overspend on: {overspend_custom or overspend}.
I impulse buy: {impulse.lower()}.
My income is: {income_stability.lower()}.
I save about: {savings_percent} of my income.
Emergency fund status: {emergency_fund}.
Confidence in managing money: {confidence}.
I want to learn about: {', '.join(topics_to_learn) if topics_to_learn else 'not specified'}.
"""

prompt = f"""
I'm building a monthly budget and would like financial advice.

- My monthly income: ${income}
- My expenses: {formatted_expenses}
- My situation: {survey_summary}

Please provide:
1. A brief financial summary, not incredibly long
2. A few bullet-point tips for the goals I want to achieve, based on every detail so far as well as {survey_summary}
3. A final motivational or educational tip

Keep the advice clear and easy to scan — avoid long paragraphs.
"""

if st.button("Get Advice"):
    with st.spinner("Asking Gemini..."):
        result = get_budget_advice(prompt)
        st.success("Here’s your advice:")
        st.markdown("### 💡 Gemini’s Personalized Financial Advice")
        st.markdown(result)



