from app import app
from exceptions import CantGetRates

from dataclasses import dataclass
from datetime import datetime
import requests


class Transfer():
    sending_country_id: str = 'RUS'
    sending_currency_id: int = 810
    receiving_country_id: str = 'TUR'
    receiving_currency_id = 840
    paid_notification_enabled: bool = 1
    receiving_amount: int = 1
    payment_method: str = 'debitCard'
    receiving_method: str = 'cash'


@dataclass
class Rate():
    dt: datetime = None
    sending_country_id: str = 'RUS'
    sending_currency_id: int = 810
    receiving_country_id: str = 'TUR'
    receiving_currency_id = 840
    paid_notification_enabled: bool = 0
    receiving_amount: int = 1
    payment_method: str = 'debitCard'
    receiving_method: str = 'cash'

    exchange_rate: float = 0.0

    def _get_current_rate_response(self) -> requests.Response:
        url = app.config['KORONAPAY_TRANSERS_TARIFFS_TEMPLATE_URL'].format(
            sending_country_id=self.sending_country_id,
            sending_currency_id=self.sending_currency_id,
            receiving_country_id=self.receiving_country_id,
            receiving_currency_id=self.receiving_currency_id,
            paid_notification_enabled=self.paid_notification_enabled,
            receiving_amount=self.receiving_amount,
            payment_method=self.payment_method,
            receiving_method=self.receiving_method
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

    def get_current_rate(self) -> None:
        try:
            curr_rate_response = self._get_current_rate_response()
            self.exchange_rate = float(
                curr_rate_response.json()[0]['exchangeRate'])
            self.dt = datetime.today()
        except:
            raise CantGetRates

    def save_to_db(self):
        pass

    def __post_init__(self) -> None:
        self.get_current_rate()
