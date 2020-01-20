from .api_client import ApiClient

import datetime
import logging

LOGGER = logging.getLogger(__name__)

def get_quarter_dates(quarter, year=None):
    '''Returns the start_date and end_date of a quarter for a given year
    or the current year.'''
    year = year or datetime.date.today().year

    if quarter == 1:
        return [f'{year}-01-01', f'{year}-03-31']
    elif quarter == 2:
        return [f'{year}-01-01', f'{year}-06-30']
    elif quarter == 3:
        return [f'{year}-07-01', f'{year}-09-30']
    elif quarter == 4:
        return [f'{year}-10-01', f'{year}-12-31']
    else:
        raise ValueError('Invalid quarter specified')
       

class CohortReport:
    name = 'Cohort'

    @staticmethod
    def get(config, quarter, year):
        '''Retrieve quarterly cohort report for a given year.'''
        start_date, end_date = get_quarter_dates(quarter, year)
        return ApiClient.get(config, 'programs/1/reports/cohort', start_date=start_date, end_date=end_date)


class MohDisaggregatedReport:
    name = 'MOH Disaggregated Report'

    @staticmethod
    def get(api_url, quarter, year):
        '''Retrieve quarterly MOH disaggregated cohort report for a given year.'''
        pass


class PepfarDisaggregatedReport:
    name = 'PEPFAR Disaggregated Report'

    @staticmethod
    def get(api_url, quarter, year):
        '''Retrieve quarterly PEPFAR disaggregated cohort report for a given year.'''
        pass

def reports():
    '''Returns a list of all EMR API reports.'''
    return [CohortReport, MohDisaggregatedReport, PepfarDisaggregatedReport]
