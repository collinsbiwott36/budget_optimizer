import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# --- Smart Optimization Function ---
def optimize_budget(income, categories, raw_utilities, allocation_ratios, min_spending, savings_target):
    model = LpProblem(name="budget_optimization", sense=LpMaximize)

    # Adjust utility weights based on income level
    def scale_utility(rating):
        # Base normalized score (1–10 → 0.5 to 1.5)
        base = 0.5 + (rating - 1) * (1.0 / 9)
        # Income tier scaling
        if income < 10000:
            return base * 0.7
        elif income < 30000:
            return base * 0.9
        else:
            return base * 1.1

    utilities = {cat: scale_utility(raw_utilities[cat]) for cat in categories}

    # Special Rent logic
    if raw_utilities["Rent"] <= 2:
        allocation_ratios["Rent"] = 0.01
        min_spending["Rent"] = 0
        utilities["Rent"] = 0
        # Slight boost to others
        for cat in categories:
            if cat != "Rent":
                utilities[cat] += 0.1

    # Define spend variables
    spend_vars = {
        cat: LpVariable(
            name=cat,
            lowBound=min_spending[cat],
            upBound=income * allocation_ratios[cat],
            cat="Continuous"
        ) for cat in categories
    }

    model += lpSum(spend_vars[cat] for cat in categories) == income, "Full_Budget_Use"
    model += lpSum(spend_vars[cat] * utilities[cat] for cat in categories), "Maximize_Utility"

    essentials = ["Food", "Savings", "Health", "Transport", "Electricity", "Water"]
    for cat in essentials:
        model += spend_vars[cat] >= min_spending[cat], f"Min_{cat}"

    if raw_utilities["Rent"] > 2:
        model += spend_vars["Rent"] >= min_spending["Rent"], "Min_Rent"

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

# New categories added
categories = ["Rent", "Food", "Savings", "Entertainment", "Transport", "Health", "Electricity", "Water", "Black Tax"]

st.sidebar.markdown("### Rate Categories (1–10)")
utilities = {cat: st.sidebar.slider(cat, 1, 10, 5) for cat in categories}

allocation_ratios = {
    "Rent": 0.25, "Food": 0.15, "Savings": 0.15,
    "Entertainment": 0.10, "Transport": 0.10,
    "Health": 0.10, "Electricity": 0.05,
    "Water": 0.05, "Black Tax": 0.05
}

min_spending = {cat: income * allocation_ratios[cat] * 0.5 for cat in categories}

# --- Run Optimization ---
if st.sidebar.button("Optimize Budget"):
    budget_allocation = optimize_budget(income, categories, utilities, allocation_ratios, min_spending, savings_target)
    budget_df = pd.DataFrame(list(budget_allocation.items()), columns=["Category", "Allocated Amount"])

    st.subheader("📊 Optimized Budget Table")
    st.dataframe(budget_df.style.format({"Allocated Amount": "Kshs {:,.2f}"}))

    # Bar Chart
    st.subheader("📈 Bar Chart")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(budget_allocation.keys(), budget_allocation.values(), color='teal')
    ax1.set_ylabel("Amount (Kshs)")
    ax1.set_title("Optimized Budget Allocation")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    pie_data = {k: v for k, v in budget_allocation.items() if v > 0}
    fig2, ax2 = plt.subplots()
    ax2.pie(pie_data.values(), labels=pie_data.keys(), autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

    # Downloadable CSV
    csv = budget_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Budget CSV", csv, "optimized_budget.csv", "text/csv")
