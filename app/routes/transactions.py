
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date

from app import db
from app.models.transaction import Transaction

transactions = Blueprint("transactions", __name__)


@transactions.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions_home():

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", "")
        transaction_type = request.form.get("transaction_type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        transaction_date = request.form.get("date")

        if not title or not amount or not transaction_type or not category:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("transactions.transactions_home"))

        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError

            selected_date = (
                datetime.strptime(transaction_date, "%Y-%m-%d").date()
                if transaction_date
                else date.today()
            )
        except ValueError:
            flash("Enter a valid positive amount and date.", "danger")
            return redirect(url_for("transactions.transactions_home"))

        if transaction_type not in ["Income", "Expense"]:
            flash("Invalid transaction type.", "danger")
            return redirect(url_for("transactions.transactions_home"))

        new_transaction = Transaction(
            user_id=current_user.id,
            title=title,
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            description=description,
            date=selected_date
        )

        db.session.add(new_transaction)
        db.session.commit()

        flash("Transaction added successfully!", "success")
        return redirect(url_for("transactions.transactions_home"))

    all_transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .all()
    )

    return render_template(
        "transactions.html",
        transactions=all_transactions,
        today=date.today().isoformat()
    )


@transactions.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        transaction_type = request.form.get("transaction_type")
        category = request.form.get("category")
        description = request.form.get("description", "").strip()
        transaction_date = request.form.get("date", "").strip()

        if not title or not amount_text or not transaction_type or not category:
            flash("Please fill in all required fields.", "danger")
            return redirect(
                url_for("transactions.edit_transaction",
                        transaction_id=transaction.id)
            )

        try:
            amount = float(amount_text)

            if amount <= 0:
                raise ValueError

            selected_date = (
                datetime.strptime(transaction_date, "%Y-%m-%d").date()
                if transaction_date
                else date.today()
            )

        except ValueError:
            flash("Enter a valid positive amount and date.", "danger")
            return redirect(
                url_for("transactions.edit_transaction",
                        transaction_id=transaction.id)
            )

        if transaction_type not in ["Income", "Expense"]:
            flash("Invalid transaction type.", "danger")
            return redirect(
                url_for("transactions.edit_transaction",
                        transaction_id=transaction.id)
            )

        transaction.title = title
        transaction.amount = amount
        transaction.transaction_type = transaction_type
        transaction.category = category
        transaction.description = description
        transaction.date = selected_date

        db.session.commit()

        flash("Transaction updated successfully!", "success")
        return redirect(url_for("transactions.transactions_home"))

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )


@transactions.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("transactions.transactions_home"))
