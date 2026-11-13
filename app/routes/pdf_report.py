import io
from datetime import date, datetime

from flask import Blueprint, Response
from flask_login import login_required, current_user
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

pdf_report = Blueprint("pdf_report", __name__)


@pdf_report.route("/download-report")
@login_required
def download_report():

    transactions = list(current_user.transactions)

    income = sum(
        float(t.amount)
        for t in transactions
        if str(t.transaction_type).lower() == "income"
    )

    expenses = sum(
        float(t.amount)
        for t in transactions
        if str(t.transaction_type).lower() == "expense"
    )

    balance = income - expenses

    category_totals = {}

    for t in transactions:
        if str(t.transaction_type).lower() == "expense":
            category_totals[t.category] = (
                category_totals.get(t.category, 0)
                + float(t.amount)
            )

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("AI Finance Assistant - Financial Report",
                  styles["Title"])
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated on: {date.today()}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    summary = [
        ["Financial Summary", "Amount (INR)"],
        ["Total Income", f"Rs. {income:,.2f}"],
        ["Total Expenses", f"Rs. {expenses:,.2f}"],
        ["Remaining Balance", f"Rs. {balance:,.2f}"]
    ]

    table = Table(summary, colWidths=[250, 200])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 10)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    elements.append(
        Paragraph("Category-wise Expenses", styles["Heading2"])
    )

    category_data = [["Category", "Amount (INR)"]]

    for category, amount in category_totals.items():
        category_data.append([
            category,
            f"Rs. {amount:,.2f}"
        ])

    category_table = Table(
        category_data,
        colWidths=[250, 200]
    )

    category_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    elements.append(category_table)
    elements.append(Spacer(1, 25))

    elements.append(
        Paragraph("Transaction History", styles["Heading2"])
    )

    transaction_data = [
        ["Date", "Category", "Type", "Amount"]
    ]

    for t in transactions:
        transaction_data.append([
            str(t.date),
            str(t.category),
            str(t.transaction_type),
            f"Rs. {float(t.amount):,.2f}"
        ])

    transaction_table = Table(
        transaction_data,
        repeatRows=1,
        colWidths=[100, 130, 90, 110]
    )

    transaction_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))

    elements.append(transaction_table)

    document.build(elements)

    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=financial_report.pdf"
        }
    )