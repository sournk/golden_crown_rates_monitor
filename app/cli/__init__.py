from flask import Blueprint
from ..models import RatesStateHandler

bp = Blueprint('cli', __name__)


@bp.cli.command()
def update_rates():
    ''' Makes request to Korona.API and saves result to DB.'''
    rates_state_handler = RatesStateHandler()
    rates_state_handler.save_to_db(rates_state_handler.get_state_from_api())


@bp.cli.command()
def test_first():
    rates_state_handler = RatesStateHandler()

    rs = rates_state_handler.get_state_from_api()
    assert rs.updated != None
