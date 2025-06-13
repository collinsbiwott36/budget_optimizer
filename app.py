import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# --- Optimization Function ---
def optimize_budget(income, categories, utilities, allocation_ratios, min_spending, savings_target):
    model = LpProblem(name="budget_optimization", sense=LpMaximize)

    spend_vars = {
        cat: LpVariable(
            name=cat,
            lowBound=min_spending[cat],
            upBound=income * allocation_ratios[cat],
            cat="Continuous"
        ) for cat in categories
    }

    model += lpSum(spend_vars[cat] * utilities[cat] for cat in categories), "Total_Utility"
    model += lpSum(spend_vars[cat] for cat in categories) <= income, "Budget_Limit"

    for cat in ["Rent", "Food", "Savings", "Health", "Transport"]:
        model += spend_vars[cat] >= min_spending[cat], f"Min_{cat}"

    model += spend_vars["Savings"] >= savings_target, "Savings_Target"

    if income < 8000:
        model += spend_vars["Entertainment"] == 0, "No_Entertainment_If_Low_Income"

    model.solve()

    return {cat: spend_vars[cat].value() for cat in categories}

# --- Streamlit App ---
st.title("💰 Personal Budget Optimizer")

st.sidebar.header("Enter Your Financial Info")

income = st.sidebar.number_input("Monthly Income (Kshs)", min_value=1000.0, value=20000.0, step=500.0)
savings_target = st.sidebar.number_input("Savings Target (Kshs)", min_value=0.0, value=3000.0)

categories = ["Rent", "Food", "Savings", "Entertainment", "Transport", "Health"]

st.sidebar.markdown("### Rate Categories (1–10)")
utilities = {cat: st.sidebar.slider(cat, 1, 10, 5) for cat in categories}

allocation_ratios = {
    "Rent": 0.30, "Food": 0.20, "Savings": 0.20,
    "Entertainment": 0.10, "Transport": 0.10, "Health": 0.10
}
min_spending = {cat: income * allocation_ratios[cat] * 0.5 for cat in categories}

if st.sidebar.button("Optimize Budget"):
    budget_allocation = optimize_budget(income, categories, utilities, allocation_ratios, min_spending, savings_target)
    budget_df = pd.DataFrame(list(budget_allocation.items()), columns=["Category", "Allocated Amount"])

    st.subheader("📊 Optimized Budget Table")
    st.dataframe(budget_df.style.format({"Allocated Amount": "Kshs {:,.2f}"}))

    # Bar Chart
    st.subheader("📈 Bar Chart")
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(budget_allocation.keys(), budget_allocation.values(), color='skyblue')
    ax1.set_ylabel("Amount (Kshs)")
    ax1.set_title("Optimized Budget Allocation")
    st.pyplot(fig1)

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    fig2, ax2 = plt.subplots()
    ax2.pie(budget_allocation.values(), labels=budget_allocation.keys(), autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

    # Downloadable CSV
    csv = budget_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Budget CSV", csv, "optimized_budget.csv", "text/csv")
