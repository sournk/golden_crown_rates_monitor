from datetime import datetime, time, timedelta

import requests
from pydantic import BaseModel

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from app import app
from exceptions import CantGetRatesFromAPI, SaveRatesToDBError, LoadRatesFromDBError


class Transfer(BaseModel):
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


class Rate(BaseModel):
    transfer: Transfer
    dt: datetime = datetime.now()
    exchange_rate: float = 0.0

    def _get_current_rate_response(self) -> requests.Response:
        url = app.config['KORONAPAY_TRANSFERS_TARIFFS_TEMPLATE_URL'].format(
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
                raise CantGetRatesFromAPI
            return res
        except:
            raise CantGetRatesFromAPI

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
            raise CantGetRatesFromAPI

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class RatesState(BaseModel):
    updated: datetime = None
    rates: list[Rate] = None


class RatesStateHandler():
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Init special TinyDb serializer for datetime
        # Overwise you cann't serialize obj with datetime fields
        self._db_serialization = SerializationMiddleware(JSONStorage)
        self._db_serialization.register_serializer(
            DateTimeSerializer(), 'TinyDate')

        self._db = TinyDB(app.config['DB'], storage=self._db_serialization)

    def save_to_db(self, rate_state: RatesState) -> None:
        try:
            self._db.insert(rate_state.dict())
        except Exception as e:
            raise SaveRatesToDBError

    def get_state_from_db(self) -> RatesState:
        try:
            # get last obj from db
            el = self._db.all()[-1]
            return RatesState.parse_obj(el)
        except Exception as e:
            raise LoadRatesFromDBError

    def get_state_from_api(self) -> RatesState:
        # if not self.updated or datetime.today() - self.updated > timedelta(seconds=app.config['REQUEST_CACHE_TIMEOUT_SEC']):
        try:
            rates = [Rate(transfer=t) for t in transfers_to_monitor]
            for r in rates:
                r.get_current_rate()

            return RatesState(updated=datetime.today(), rates=rates)
        except Exception as e:
            raise CantGetRatesFromAPI

    def get_rates_state_list(self, depth_days: int = 31) -> list[RatesState]:

        def _get_rates_state_list_from_db_by_period() -> list:
            ''' 
                Get all rates states from db by period. 
                List includes rates for every hour or often (see crontab) 
            '''
            date_end = datetime.combine(datetime.today(), time.max)
            date_start = date_end - timedelta(days=depth_days-1)
            date_start = datetime.combine(date_start, time.min)

            q = Query()
            result_list = self._db.search(
                (q.updated >= date_start) & (q.updated <= date_end))
            return [RatesState.parse_obj(li) for li in result_list]

        def _get_dict_of_max_rates_in_day(rate_state_list: list[RatesState]) -> dict[datetime.date, Rate]:
            '''
                Leaves in list only rates_state with max value for each currency
            '''
            # todo: list нужно отсортировать по дате, иначе возможны проблемы
            rd = {}
            for rs in rates_state_list:
                day_rates = rd.get(rs.updated.date(), {})
                for r in rs.rates:
                    old_rate = day_rates.get(r.transfer.id, None)
                    old_rate = old_rate.exchange_rate if old_rate != None else 0
                    if r.exchange_rate > old_rate:
                        day_rates[r.transfer.id] = r

                rd[rs.updated.date()] = day_rates

            return rd

        rates_state_list = _get_rates_state_list_from_db_by_period()
        rd = _get_dict_of_max_rates_in_day(rates_state_list)

        # Now rd has dict of Rate by date
        # Convert rd to list of RatesState
        return [RatesState(
            updated=datetime.combine(k, time.min),
            rates=list(v.values())) for k, v in rd.items()]


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
