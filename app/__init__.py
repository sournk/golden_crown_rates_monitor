from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config())

from app import routes
from app.models import rates_state


@app.cli.command()
def update_rates():
    ''' Makes request to Korona.API and saves result to DB.'''
    rates_state.update()
    rates_state.save_to_db()
