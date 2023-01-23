import click
import pandas as pd
from flask import Blueprint, current_app
from ..models import RatesStateHandler

bp = Blueprint('cli', __name__)


@bp.cli.command()
def update_rates():
    ''' Makes request to Korona.API and saves result to DB.'''
    rates_state_handler = RatesStateHandler()
    rates_state_handler.save_to_db(rates_state_handler.get_state_from_api())


@bp.cli.command()
@click.argument('filename')
def analytics_save_daily_rates_of_lastmonth_to_csv(filename: str) -> None:
    """ Convert data from TinyDB to CSV for convenient pandas analitics.

    Args:
        filename (str): filename to save CSV
    """

    rates_state_handle = RatesStateHandler()
    rates_state_list = rates_state_handle.get_rates_state_list()
    rates_state_list = [r.dict() for r in rates_state_list]

    import pandas as pd

    df = pd.json_normalize(rates_state_list, "rates", ["updated"])
    df.to_csv(filename)

    current_app.logger.info(f'Last month daily rates saved to file {filename}')


@bp.cli.command()
def test_first():
    rates_state_handler = RatesStateHandler()

    rs = rates_state_handler.get_state_from_api()
    assert rs.updated != None
