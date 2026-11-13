
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, datetime
from collections import defaultdict

analytics = Blueprint("analytics", __name__)


@analytics.route("/analytics")
@login_required
def analytics_home():

    today = date.today()
    transactions = current_user.transactions

    # Last six months
    months = []

    for i in range(5, -1, -1):
        month_number = today.month - i
        year = today.year

        while month_number <= 0:
            month_number += 12
            year -= 1

        months.append((year, month_number))

    month_labels = [
        date(year, month, 1).strftime("%b %Y")
        for year, month in months
    ]

    monthly_income = []
    monthly_expenses = []

    category_spending = defaultdict(float)

    for year, month in months:

        income = 0
        expenses = 0

        for transaction in transactions:

            transaction_date = transaction.date

            if isinstance(transaction_date, datetime):
                transaction_date = transaction_date.date()

            if isinstance(transaction_date, str):
                try:
                    transaction_date = date.fromisoformat(
                        transaction_date[:10]
                    )
                except ValueError:
                    continue

            if not transaction_date:
                continue

            if (
                transaction_date.year == year
                and transaction_date.month == month
            ):

                amount = float(transaction.amount)

                transaction_type = str(
                    transaction.transaction_type
                ).lower()

                if transaction_type == "income":
                    income += amount

                elif transaction_type == "expense":
                    expenses += amount

                    if year == today.year and month == today.month:
                        category = transaction.category or "Other"
                        category_spending[category] += amount

        monthly_income.append(round(income, 2))
        monthly_expenses.append(round(expenses, 2))

    current_income = monthly_income[-1]
    current_expenses = monthly_expenses[-1]

    current_balance = current_income - current_expenses

    six_month_income = sum(monthly_income)
    six_month_expenses = sum(monthly_expenses)

    category_labels = list(category_spending.keys())

    category_values = [
        round(value, 2)
        for value in category_spending.values()
    ]

    highest_category = (
        max(category_spending, key=category_spending.get)
        if category_spending else "No expenses"
    )

    chart_data = {
        "months": month_labels,
        "income": monthly_income,
        "expenses": monthly_expenses,
        "categories": category_labels,
        "category_amounts": category_values
    }

    return render_template(
        "analytics.html",
        chart_data=chart_data,
        current_income=current_income,
        current_expenses=current_expenses,
        current_balance=current_balance,
        highest_category=highest_category,
        six_month_income=six_month_income,
        six_month_expenses=six_month_expenses
    )
