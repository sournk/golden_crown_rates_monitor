from app import app
from flask import render_template, abort
from app.models import RatesStateHandler


@app.route('/rates')
def rates():
    pass


@app.route('/')
def index():
    try:
        rates_state_handler = RatesStateHandler()
        rates_state = rates_state_handler.get_state_from_db()
        return render_template('index.html', rates_state=rates_state.dict())
    except Exception as e:
        abort(500)
