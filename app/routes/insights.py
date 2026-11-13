from flask import Blueprint, render_template
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import date

insights = Blueprint("insights", __name__)


@insights.route("/insights")
@login_required
def insights_home():

    today = date.today()

    transactions = current_user.transactions

    monthly_transactions = [
        t for t in transactions
        if t.date and t.date.month == today.month
        and t.date.year == today.year
    ]

    income = sum(
        float(t.amount)
        for t in monthly_transactions
        if str(t.transaction_type).lower() == "income"
    )

    expenses = sum(
        float(t.amount)
        for t in monthly_transactions
        if str(t.transaction_type).lower() == "expense"
    )

    balance = income - expenses

    category_spending = defaultdict(float)

    for transaction in monthly_transactions:
        if str(transaction.transaction_type).lower() == "expense":
            category_spending[transaction.category] += float(
                transaction.amount
            )

    sorted_categories = sorted(
        category_spending.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_category = (
        sorted_categories[0][0]
        if sorted_categories else "No expenses yet"
    )

    insights_list = []

    if income == 0 and expenses == 0:
        insights_list.append({
            "title": "Start tracking your finances",
            "message": "Add income and expense transactions to receive financial insights.",
            "type": "info"
        })

    if income > 0:

        savings_percentage = (balance / income) * 100

        if balance > 0:
            insights_list.append({
                "title": "Positive financial balance",
                "message": f"You have ₹{balance:,.2f} remaining this month.",
                "type": "success"
            })

        elif balance < 0:
            insights_list.append({
                "title": "Expenses exceed income",
                "message": "Your recorded expenses are higher than your income. Review your spending.",
                "type": "warning"
            })

        else:
            insights_list.append({
                "title": "Income fully utilized",
                "message": "Your recorded income and expenses are equal.",
                "type": "warning"
            })

        if savings_percentage >= 20:
            insights_list.append({
                "title": "Good savings progress",
                "message": f"Your remaining balance is {savings_percentage:.1f}% of your income.",
                "type": "success"
            })

        elif balance >= 0:
            insights_list.append({
                "title": "Savings opportunity",
                "message": "Consider reviewing optional expenses and setting a realistic savings goal.",
                "type": "info"
            })

    if sorted_categories:
        amount = sorted_categories[0][1]

        insights_list.append({
            "title": "Highest spending category",
            "message": f"{top_category}: ₹{amount:,.2f}",
            "type": "info"
        })

    if expenses > 0:
        for category, amount in sorted_categories:
            percentage = amount / expenses * 100

            if percentage >= 40:
                insights_list.append({
                    "title": f"Review {category} spending",
                    "message": f"This category accounts for {percentage:.1f}% of your expenses.",
                    "type": "warning"
                })

    recommendations = [
        "Track your daily expenses consistently.",
        "Review your highest spending category.",
        "Set realistic monthly budgets.",
        "Compare your income and expenses regularly.",
        "Plan optional purchases before spending."
    ]

    return render_template(
        "insights.html",
        income=income,
        expenses=expenses,
        balance=balance,
        top_category=top_category,
        category_spending=sorted_categories,
        insights_list=insights_list,
        recommendations=recommendations,
        month_name=today.strftime("%B %Y")
    )