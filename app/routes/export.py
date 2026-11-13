import csv
import io

from flask import Blueprint, Response
from flask_login import login_required, current_user

export = Blueprint("export", __name__)


@export.route("/export/transactions")
@login_required
def export_transactions():

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Title",
        "Category",
        "Type",
        "Amount"
    ])

    transactions = current_user.transactions

    for transaction in transactions:
        writer.writerow([
            transaction.date,
            getattr(transaction, "title", ""),
            transaction.category,
            transaction.transaction_type,
            transaction.amount
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=financial_transactions.csv"
    )

    return response