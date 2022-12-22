class CantGetRatesFromAPI(Exception):
    ''' Error getting rates from koronapay.ru'''
    pass


class SaveRatesToDBError(Exception):
    ''' Can't save to db '''
    pass


class LoadRatesFromDBError(Exception):
    ''' Can't save to db '''
    pass