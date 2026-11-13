from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Authentication
    from app.routes.auth import auth
    app.register_blueprint(auth)

    # Dashboard
    from app.routes.dashboard import dashboard
    app.register_blueprint(dashboard)

    # Transactions
    from app.routes.transactions import transactions
    app.register_blueprint(transactions)

    # Budget Management
    from app.routes.budgets import budgets
    app.register_blueprint(budgets)

    # AI Financial Insights
    from app.routes.insights import insights
    app.register_blueprint(insights)

    # Advanced Analytics
    from app.routes.analytics import analytics
    app.register_blueprint(analytics)

    # Finance Chatbot
    from app.routes.chatbot import chatbot
    app.register_blueprint(chatbot)

    # CSV Export
    from app.routes.export import export
    app.register_blueprint(export)

    # PDF Financial Report
    from app.routes.pdf_report import pdf_report
    app.register_blueprint(pdf_report)

    # Recurring Transactions
    from app.routes.recurring import recurring
    app.register_blueprint(recurring)

    # Financial Goals
    from app.routes.goals import goals
    app.register_blueprint(goals)

    # Create database tables
    with app.app_context():
        from app.models import user, transaction, budget, recurring_transaction
        from app.models.savings_goal import SavingsGoal

        db.create_all()
        
    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return db.session.get(User, int(user_id))