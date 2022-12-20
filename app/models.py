from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from pydantic import BaseModel

from app import app
from exceptions import CantGetRates


@dataclass
class Transfer():
    id: int
    sending_country_id: str = 'RUS'
    sending_currency_id: int = 810
    sending_currency_code: str = None  # Ex='RUB'
    sending_currency_name: str = None  # Ex='Российский рубль'

    receiving_country_id: str = 'TUR'
    receiving_currency_id: int = 840
    receiving_currency_code: str = None  # Ex='USD'
    receiving_currency_name: str = None  # Ex='Доллар США'

    paid_notification_enabled: bool = 1
    receiving_amount: int = 100
    payment_method: str = 'debitCard'
    receiving_method: str = 'cash'


@dataclass
class Rate():
    transfer: Transfer
    dt: datetime = datetime.now()
    exchange_rate: float = 0.0

    def _get_current_rate_response(self) -> requests.Response:
        url = app.config['KORONAPAY_TRANSERS_TARIFFS_TEMPLATE_URL'].format(
            sending_currency_id=self.transfer.sending_currency_id,
            sending_country_id=self.transfer.sending_country_id,
            receiving_country_id=self.transfer.receiving_country_id,
            receiving_currency_id=self.transfer.receiving_currency_id,
            paid_notification_enabled=self.transfer.paid_notification_enabled,
            receiving_amount=self.transfer.receiving_amount,
            payment_method=self.transfer.payment_method,
            receiving_method=self.transfer.receiving_method
        )

        try:
            headers = {
                'User-Agent': app.config['REQUEST_USER_AGENT']}
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                raise CantGetRates
            return res
        except:
            raise CantGetRates

    def _update_transfer_labels(self,
                                sending_currency_code: str,
                                sending_currency_name: str,
                                receiving_currency_code: str,
                                receiving_currency_name: str) -> None:
        ''' Update Transfer fields with sending and reciving currencies labels '''
        self.transfer.sending_currency_code = sending_currency_code
        self.transfer.sending_currency_name = sending_currency_name

        self.transfer.receiving_currency_code = receiving_currency_code
        self.transfer.receiving_currency_name = receiving_currency_name

    def get_current_rate(self) -> None:
        try:
            curr_rate_response = self._get_current_rate_response()
            self.exchange_rate = float(
                curr_rate_response.json()[0]['exchangeRate'])
            self._update_transfer_labels(
                curr_rate_response.json()[0]['sendingCurrency']['code'],
                curr_rate_response.json()[0]['sendingCurrency']['name'],
                curr_rate_response.json()[0]['receivingCurrency']['code'],
                curr_rate_response.json()[0]['receivingCurrency']['name'])
            self.dt = datetime.today()
        except:
            raise CantGetRates

    def save_to_db(self):
        pass

    def __post_init__(self) -> None:
        self.get_current_rate()


class RatesState(BaseModel):
    updated: datetime = None
    rates: list[Rate] = None

    def update(self) -> None:
        if not self.updated or datetime.today() - self.updated > timedelta(seconds=app.config['REQUEST_CACHE_TIMEOUT_SEC']):
            try:
                self.rates = [Rate(t) for t in transfers_to_monitor]
                self.updated = datetime.today()
            except:
                raise CantGetRates


transfers_to_monitor = [
    # RUB->USD from RUS->TUR
    Transfer(
        id=1,
        sending_country_id='RUS',
        sending_currency_id=810,
        receiving_country_id='TUR',
        receiving_currency_id=840,
        paid_notification_enabled=True,
        payment_method='debitCard',
        receiving_method='cash'),

    # RUB->TRY from RUS->TUR
    Transfer(
        id=2,
        sending_country_id='RUS',
        sending_currency_id=810,
        receiving_country_id='TUR',
        receiving_currency_id=949,
        paid_notification_enabled=True,
        payment_method='debitCard',
        receiving_method='cash')]

rates_state = RatesState()
