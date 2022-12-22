from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config())

from app import routes
from app.models import RatesStateHandler


@app.cli.command()
def update_rates():
    ''' Makes request to Korona.API and saves result to DB.'''
    rates_state_handler = RatesStateHandler()
    rates_state_handler.save_to_db(rates_state_handler.get_state_from_api())
