
import calendar

from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.transaction import Transaction
from app.models.recurring_transaction import RecurringTransaction


recurring = Blueprint("recurring", __name__)


def add_months(original_date, months, anchor_day=None):
    month_index = original_date.month - 1 + months

    year = original_date.year + month_index // 12
    month = month_index % 12 + 1

    day = anchor_day or original_date.day
    last_day = calendar.monthrange(year, month)[1]

    return date(year, month, min(day, last_day))


def process_due_transactions(user_id):

    today = date.today()

    recurring_items = RecurringTransaction.query.filter_by(
        user_id=user_id,
        active=True
    ).all()

    for item in recurring_items:

        count = 0

        while item.next_due_date <= today and count < 366:

            new_transaction = Transaction(
                user_id=user_id,
                title=item.title,
                amount=item.amount,
                transaction_type=item.transaction_type,
                category=item.category,
                description=item.description,
                date=item.next_due_date
            )

            db.session.add(new_transaction)

            if item.frequency == "Daily":
                item.next_due_date += timedelta(days=1)

            elif item.frequency == "Weekly":
                item.next_due_date += timedelta(weeks=1)

            elif item.frequency == "Monthly":
                item.next_due_date = add_months(
                    item.next_due_date,
                    1,
                    item.day_of_month
                )

            count += 1

    db.session.commit()


@recurring.route("/recurring", methods=["GET", "POST"])
@login_required
def recurring_home():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", "")
        transaction_type = request.form.get("transaction_type")
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        frequency = request.form.get("frequency")
        start_date = request.form.get("start_date")

        if not all([
            title, amount, transaction_type,
            category, frequency, start_date
        ]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("recurring.recurring_home"))

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

            selected_date = datetime.strptime(
                start_date, "%Y-%m-%d"
            ).date()

        except ValueError:
            flash("Enter a valid amount and date.", "danger")
            return redirect(url_for("recurring.recurring_home"))

        if transaction_type not in ["Income", "Expense"]:
            flash("Invalid transaction type.", "danger")
            return redirect(url_for("recurring.recurring_home"))

        if frequency not in ["Daily", "Weekly", "Monthly"]:
            flash("Invalid recurring frequency.", "danger")
            return redirect(url_for("recurring.recurring_home"))

        new_recurring = RecurringTransaction(
            user_id=current_user.id,
            title=title,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            description=description,
            frequency=frequency,
            next_due_date=selected_date,
            day_of_month=selected_date.day
        )

        db.session.add(new_recurring)
        db.session.commit()

        # Add the transaction immediately if its due date has arrived.
        process_due_transactions(current_user.id)

        flash("Recurring transaction added successfully!", "success")

        return redirect(url_for("recurring.recurring_home"))

    # Process any transactions that have become due.
    process_due_transactions(current_user.id)

    recurring_items = RecurringTransaction.query.filter_by(
        user_id=current_user.id
    ).order_by(
        RecurringTransaction.next_due_date.asc()
    ).all()

    return render_template(
        "recurring.html",
        recurring_items=recurring_items,
        today=date.today().isoformat()
    )


@recurring.route("/recurring/toggle/<int:recurring_id>", methods=["POST"])
@login_required
def toggle_recurring(recurring_id):

    item = RecurringTransaction.query.filter_by(
        id=recurring_id,
        user_id=current_user.id
    ).first_or_404()

    item.active = not item.active

    db.session.commit()

    flash(
        "Recurring transaction updated successfully.",
        "success"
    )

    return redirect(url_for("recurring.recurring_home"))


@recurring.route("/recurring/delete/<int:recurring_id>", methods=["POST"])
@login_required
def delete_recurring(recurring_id):

    item = RecurringTransaction.query.filter_by(
        id=recurring_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("Recurring transaction deleted.", "success")

    return redirect(url_for("recurring.recurring_home"))
