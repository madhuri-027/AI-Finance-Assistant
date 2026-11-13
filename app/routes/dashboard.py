
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date
from collections import defaultdict

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@login_required
def dashboard_home():

    all_transactions = current_user.transactions

    # Calculate total income and expenses
    total_income = sum(
        t.amount for t in all_transactions
        if t.transaction_type == "Income"
    )

    total_expenses = sum(
        t.amount for t in all_transactions
        if t.transaction_type == "Expense"
    )

    balance = total_income - total_expenses

    # Current month transactions
    today = date.today()

    monthly_transactions = [
        t for t in all_transactions
        if t.date.month == today.month
        and t.date.year == today.year
    ]

    monthly_income = sum(
        t.amount for t in monthly_transactions
        if t.transaction_type == "Income"
    )

    monthly_expenses = sum(
        t.amount for t in monthly_transactions
        if t.transaction_type == "Expense"
    )

    # Category-wise expense analysis
    category_totals = defaultdict(float)

    for t in all_transactions:
        if t.transaction_type == "Expense":
            category_totals[t.category] += t.amount

    category_labels = list(category_totals.keys())
    category_values = list(category_totals.values())

    # Last six months analysis
    month_labels = []
    income_data = []
    expense_data = []

    for i in range(5, -1, -1):

        month = today.month - i
        year = today.year

        while month <= 0:
            month += 12
            year -= 1

        month_labels.append(date(year, month, 1).strftime("%b %Y"))

        month_items = [
            t for t in all_transactions
            if t.date.month == month and t.date.year == year
        ]

        income_data.append(
            sum(t.amount for t in month_items
                if t.transaction_type == "Income")
        )

        expense_data.append(
            sum(t.amount for t in month_items
                if t.transaction_type == "Expense")
        )

    # Recent transactions
    recent_transactions = sorted(
        all_transactions,
        key=lambda t: (t.date, t.id),
        reverse=True
    )[:5]

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        category_labels=category_labels,
        category_values=category_values,
        month_labels=month_labels,
        income_data=income_data,
        expense_data=expense_data,
        recent_transactions=recent_transactions,
        today=today
    )
