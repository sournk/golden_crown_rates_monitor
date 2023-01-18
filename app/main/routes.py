from flask import render_template, abort, jsonify, current_app
from app.models import RatesStateHandler
from app.main import bp


@bp.route('/rates')
def rates():
    '''
        API endpoint returns JSON with rates stats for 31 days by default
    '''

    rates_state_list = RatesStateHandler().get_rates_state_list(
        current_app.config['RATES_STATE_STATS_DEPTH_DAYS'])
    return jsonify([rs.dict() for rs in rates_state_list])


@bp.route('/')
def index():
    try:
        rates_state_handler = RatesStateHandler()
        rates_state = rates_state_handler.get_state_from_db()
        return render_template('index.html', rates_state=rates_state.dict())
    except Exception as e:
        abort(500)
