
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import date, datetime
from collections import defaultdict

chatbot = Blueprint("chatbot", __name__)


def get_monthly_data():
    today = date.today()
    transactions = current_user.transactions

    income = 0
    expenses = 0
    categories = defaultdict(float)

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
            transaction_date.month == today.month
            and transaction_date.year == today.year
        ):
            amount = float(transaction.amount)
            transaction_type = str(
                transaction.transaction_type
            ).lower()

            if transaction_type == "income":
                income += amount

            elif transaction_type == "expense":
                expenses += amount
                categories[transaction.category or "Other"] += amount

    return income, expenses, categories


def generate_answer(question):
    income, expenses, categories = get_monthly_data()
    balance = income - expenses

    question = question.lower().strip()

    if any(word in question for word in ["hello", "hi", "hey"]):
        return "Hello! I'm your Finance Assistant. Ask me about your income, expenses, balance or savings."

    if any(word in question for word in ["income", "salary", "earned"]):
        return f"Your total recorded income this month is ₹{income:,.2f}."

    if any(word in question for word in [
        "expense", "expenses", "spent", "spend",
        "spending", "expenditure"
    ]):
        return f"Your total recorded expenses this month are ₹{expenses:,.2f}."

    if any(word in question for word in [
        "balance", "remaining", "left", "available"
    ]):
        return (
            f"Your current monthly balance is ₹{balance:,.2f}. "
            "This is calculated as income minus expenses."
        )

    if any(word in question for word in ["saving", "savings"]):
        if income > 0:
            percentage = balance / income * 100
            return (
                f"Your current balance is ₹{balance:,.2f}, "
                f"which is {percentage:.1f}% of your recorded income."
            )
        return "You have no recorded income this month yet."

    if any(word in question for word in [
        "category", "highest", "most"
    ]):
        if categories:
            category, amount = max(
                categories.items(),
                key=lambda item: item[1]
            )
            return (
                f"Your highest spending category this month is "
                f"{category}, with ₹{amount:,.2f}."
            )
        return "You have no recorded expenses this month."

    if "budget" in question:
        return (
            "You can manage monthly category limits in Budget Management. "
            "Review your spending against your budget regularly."
        )

    if any(word in question for word in [
        "tip", "advice", "suggest", "improve"
    ]):
        return (
            "Here are some practical financial tips:\n"
            "1. Track your daily expenses.\n"
            "2. Review your highest spending category.\n"
            "3. Set realistic monthly budgets.\n"
            "4. Compare income and expenses regularly."
        )

    if any(word in question for word in ["report", "summary"]):
        return (
            f"Your monthly financial summary:\n"
            f"Income: ₹{income:,.2f}\n"
            f"Expenses: ₹{expenses:,.2f}\n"
            f"Remaining balance: ₹{balance:,.2f}."
        )

    return (
        "I can help you understand your finances. Try asking:\n"
        "• What is my income?\n"
        "• How much did I spend?\n"
        "• What is my remaining balance?\n"
        "• Which category has the highest spending?\n"
        "• Give me some saving tips."
    )


@chatbot.route("/chatbot", methods=["GET", "POST"])
@login_required
def chatbot_home():
    question = ""
    answer = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()

        if not question:
            answer = "Please enter a question."
        elif len(question) > 500:
            answer = "Please keep your question under 500 characters."
        else:
            answer = generate_answer(question)

    return render_template(
        "chatbot.html",
        question=question,
        answer=answer
    )
