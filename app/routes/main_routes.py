from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Serwuje główny interfejs użytkownika - stronę czatu.
    """
    return render_template('ask_form.html')