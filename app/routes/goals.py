
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.savings_goal import SavingsGoal

goals = Blueprint("goals", __name__)


@goals.route("/goals", methods=["GET", "POST"])
@login_required
def goals_home():

    if request.method == "POST":

        goal_name = request.form.get("goal_name", "").strip()
        target_amount = request.form.get("target_amount", type=float)
        deadline_text = request.form.get("deadline", "").strip()

        if not goal_name or target_amount is None or target_amount <= 0:
            flash("Please enter a valid goal name and target amount.", "danger")
            return redirect(url_for("goals.goals_home"))

        # Convert HTML date string into Python date object
        deadline = None

        if deadline_text:
            try:
                deadline = datetime.strptime(
                    deadline_text, "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Please enter a valid deadline.", "danger")
                return redirect(url_for("goals.goals_home"))

        goal = SavingsGoal(
            user_id=current_user.id,
            goal_name=goal_name,
            target_amount=target_amount,
            saved_amount=0.0,
            deadline=deadline
        )

        try:
            db.session.add(goal)
            db.session.commit()
            flash("Savings goal created successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Unable to create goal. Please try again.", "danger")

        return redirect(url_for("goals.goals_home"))

    goals_list = SavingsGoal.query.filter_by(
        user_id=current_user.id
    ).order_by(SavingsGoal.created_at.desc()).all()

    return render_template("goals.html", goals=goals_list)


@goals.route("/goals/add-money/<int:goal_id>", methods=["POST"])
@login_required
def add_money(goal_id):

    goal = SavingsGoal.query.filter_by(
        id=goal_id,
        user_id=current_user.id
    ).first_or_404()

    amount = request.form.get("amount", type=float)

    if amount is None or amount <= 0:
        flash("Enter a valid savings amount.", "danger")

    elif goal.saved_amount + amount > goal.target_amount:
        flash("Amount exceeds your remaining goal.", "warning")

    else:
        try:
            goal.saved_amount += amount
            db.session.commit()
            flash("Savings added successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Unable to update savings.", "danger")

    return redirect(url_for("goals.goals_home"))


@goals.route("/goals/delete/<int:goal_id>", methods=["POST"])
@login_required
def delete_goal(goal_id):

    goal = SavingsGoal.query.filter_by(
        id=goal_id,
        user_id=current_user.id
    ).first_or_404()

    try:
        db.session.delete(goal)
        db.session.commit()
        flash("Goal deleted successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to delete goal.", "danger")

    return redirect(url_for("goals.goals_home"))
