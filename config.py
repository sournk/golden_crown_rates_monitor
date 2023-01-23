import os


class Config():
    SECRET_KEY = os.getenv(
        'SECRET_KEY') or 'jL2L#B3R2UGK^xJ22dy1sDpG9GMpwDx9tbBF*zP7m4irWdORLv'

    KORONAPAY_TRANSFERS_TARIFFS_TEMPLATE_URL = ('https://koronapay.com/transfers/online/api/transfers/tariffs'
                                               '?sendingCountryId={sending_country_id}'
                                               '&sendingCurrencyId={sending_currency_id}'
                                               '&receivingCountryId={receiving_country_id}'
                                               '&receivingCurrencyId={receiving_currency_id}'
                                               '&paymentMethod={payment_method}'
                                               '&receivingAmount={receiving_amount}'
                                               '&receivingMethod={receiving_method}'
                                               '&paidNotificationEnabled={paid_notification_enabled}'
                                               )
    REQUEST_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    REQUEST_CACHE_TIMEOUT_SEC = os.getenv(
        'REQUEST_CACHE_TIMEOUT') or 5*60
    DB = os.getenv('DB') or 'db.json'
    RATES_STATE_STATS_DEPTH_DAYS = os.getenv('RATES_STATE_STATS_DEPTH_DAYS') or 31
    LOG_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "simple",
                "filename": "app.log",
                "mode": "a"
            },
            "fileRotation": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "simple",
                "filename": "app.log",
                "maxBytes": 1024*1024,
                "backupCount": 10
            }
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": [
                    "stdout",
                    "fileRotation"
                ]
            }
        }
    }

