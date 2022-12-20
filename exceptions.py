class CantGetRates(Exception):
    ''' Error getting rates from koronapay.ru'''
    pass


class SaveToDBError(Exception):
    ''' Can't save to db '''
    pass