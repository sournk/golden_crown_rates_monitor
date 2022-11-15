from app import app
from flask import render_template, abort
from app.models import Rate


@app.route('/rates')
def rates():
    

def index():
    try:
        rate = Rate()
        return render_template('index.html', var1=rate)
    except:
        abort(500)
