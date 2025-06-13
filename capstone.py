import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import pandas as pd

# Function: Optimize budget based on income, user preferences, and constraints
def optimize_budget(income, categories, utilities, allocation_ratios, min_spending, savings_target):
    model = LpProblem(name="budget_optimization", sense=LpMaximize)

    # Define LP variables
    spend_vars = {
        cat: LpVariable(
            name=cat,
            lowBound=min_spending[cat],
            upBound=income * allocation_ratios[cat],
            cat="Continuous"
        ) for cat in categories
    }

    # Objective: Maximize total utility
    model += lpSum(spend_vars[cat] * utilities[cat] for cat in categories), "Total_Utility"

    # Constraint: Total spending ≤ income
    model += lpSum(spend_vars[cat] for cat in categories) <= income, "Budget_Limit"

    # Prioritize essentials
    essentials = ["Rent", "Food", "Savings", "Health", "Transport"]
    for cat in essentials:
        model += spend_vars[cat] >= min_spending[cat], f"Min_{cat}"

    # Savings target
    model += spend_vars["Savings"] >= savings_target, "Savings_Target"

    # Eliminate entertainment if income is very low
    if income < 8000:
        model += spend_vars["Entertainment"] == 0, "No_Entertainment_If_Low_Income"

    # Solve LP problem
    model.solve()

    # Return results
    return {cat: spend_vars[cat].value() for cat in categories}


# --- User Input ---
income = float(input("Enter your monthly income (Kshs): "))
categories = ["Rent", "Food", "Savings", "Entertainment", "Transport", "Health"]

print("\nRate the importance of each category from 1 (least) to 10 (most):")
utilities = {cat: int(input(f"{cat}: ")) for cat in categories}
savings_target = float(input("\nEnter your savings target (Kshs): "))

# Allocation ratios (suggested)
allocation_ratios = {
    "Rent": 0.30, "Food": 0.20, "Savings": 0.20,
    "Entertainment": 0.10, "Transport": 0.10, "Health": 0.10
}

# Minimum spend threshold (50% of allocation ratio)
min_spending = {cat: income * allocation_ratios[cat] * 0.5 for cat in categories}

# --- Run Optimization ---
budget_allocation = optimize_budget(income, categories, utilities, allocation_ratios, min_spending, savings_target)

# --- Save & Display Results ---
# Create DataFrame
budget_df = pd.DataFrame(list(budget_allocation.items()), columns=["Category", "Allocated Amount"])

# Save table to CSV
budget_df.to_csv("optimized_budget.csv", index=False)

# Print to console
print("\nOptimized Budget Allocation:")
print(budget_df.to_string(index=False))

# --- Bar Chart ---
plt.figure(figsize=(10, 5))
plt.bar(
    budget_allocation.keys(),
    budget_allocation.values(),
    color=["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#8c564b"]
)
plt.xlabel("Spending Categories")
plt.ylabel("Allocated Budget (Kshs)")
plt.title(f"Optimized Budget Allocation for Income: Kshs {income:,.2f}")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("budget_bar_chart.png")  # Save bar chart
plt.show()

# --- Pie Chart ---
plt.figure(figsize=(7, 7))
plt.pie(
    budget_allocation.values(),
    labels=budget_allocation.keys(),
    autopct="%1.1f%%",
    colors=["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#8c564b"]
)
plt.title(f"Budget Distribution for Income: Kshs {income:,.2f}")
plt.tight_layout()
plt.savefig("budget_pie_chart.png")  # Save pie chart
plt.show()
