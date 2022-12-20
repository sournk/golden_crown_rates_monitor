from app import app
from flask import render_template, abort
from app.models import rates_state


@app.route('/rates')
def rates():
    pass


@app.route('/')
def index():
    try:
        rates_state.update()
        rates_state.save_to_db()
        return render_template('index.html', rates_state=rates_state.dict())
    except:
        abort(500)
