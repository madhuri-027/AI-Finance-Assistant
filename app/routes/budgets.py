
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import func

from app import db
from app.models.budget import Budget
from app.models.transaction import Transaction

budgets = Blueprint("budgets", __name__)


CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Education",
    "Bills",
    "Entertainment",
    "Health",
    "Other"
]


@budgets.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets_home():

    today = date.today()

    selected_month = request.values.get("month", today.month, type=int)
    selected_year = request.values.get("year", today.year, type=int)

    if not 1 <= selected_month <= 12:
        selected_month = today.month

    if not 2000 <= selected_year <= 2100:
        selected_year = today.year

    if request.method == "POST":

        category = request.form.get("category", "").strip()
        amount = request.form.get("amount", "")

        try:
            amount = float(amount)

            if category not in CATEGORIES or amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            flash("Enter a valid category and budget amount.", "danger")
            return redirect(url_for(
                "budgets.budgets_home",
                month=selected_month,
                year=selected_year
            ))

        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category=category,
            month=selected_month,
            year=selected_year
        ).first()

        if existing_budget:
            existing_budget.amount = amount
            flash("Budget updated successfully!", "success")
        else:
            new_budget = Budget(
                user_id=current_user.id,
                category=category,
                amount=amount,
                month=selected_month,
                year=selected_year
            )

            db.session.add(new_budget)
            flash("Budget created successfully!", "success")

        db.session.commit()

        return redirect(url_for(
            "budgets.budgets_home",
            month=selected_month,
            year=selected_year
        ))

    budget_records = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).order_by(Budget.category).all()

    budget_data = []

    total_budget = 0
    total_spent = 0

    for budget in budget_records:

        spent = db.session.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.transaction_type == "Expense",
            func.extract("month", Transaction.date) == selected_month,
            func.extract("year", Transaction.date) == selected_year
        ).scalar()

        spent = float(spent or 0)
        limit = float(budget.amount)

        remaining = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0

        if percentage >= 100:
            status = "Exceeded"
        elif percentage >= 80:
            status = "Warning"
        else:
            status = "On Track"

        budget_data.append({
            "id": budget.id,
            "category": budget.category,
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage,
            "status": status
        })

        total_budget += limit
        total_spent += spent

    total_remaining = total_budget - total_spent

    return render_template(
        "budget.html",
        budget_data=budget_data,
        categories=CATEGORIES,
        selected_month=selected_month,
        selected_year=selected_year,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_remaining
    )


@budgets.route("/budgets/delete/<int:budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id):

    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=current_user.id
    ).first_or_404()

    month = budget.month
    year = budget.year

    db.session.delete(budget)
    db.session.commit()

    flash("Budget deleted successfully!", "success")

    return redirect(url_for(
        "budgets.budgets_home",
        month=month,
        year=year
    ))
