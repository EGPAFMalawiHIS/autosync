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
        LOGGER.debug(f'Retrieving cohort report for Q{quarter}-{year}')
        start_date, end_date = get_quarter_dates(quarter, year)
        return ApiClient(config).get('programs/1/reports/cohort', name=f'Q{quarter}-{year}',
                                                                  start_date=start_date,
                                                                  end_date=end_date)


class MohDisaggregatedReport:
    name = 'MOH Disaggregated Report'

    @staticmethod
    def get(config, quarter, year):
        '''Retrieve quarterly MOH disaggregated cohort report for a given year.'''
        LOGGER.debug(f'Retrieving MOH disaggregated report for Q{quarter}-{year}')
        start_date, end_date = get_quarter_dates(quarter, year)
        return ApiClient(config).get('cohort_disaggregated', start_date=start_date, end_date=end_date)


class PepfarDisaggregatedReport:
    name = 'PEPFAR Disaggregated Report'

    @staticmethod
    def get(config, quarter, year):
        '''Retrieve quarterly PEPFAR disaggregated cohort report for a given year.'''
        LOGGER.debug(f'Retrieving PEPFAR disaggregated cohort report for Q{quarter}-{year}')
        return {}

def reports():
    '''Returns a list of all EMR API reports.'''
    return [CohortReport, MohDisaggregatedReport, PepfarDisaggregatedReport]


if __name__ == '__main__':
    config = {'emr_api_host': 'localhost',
              'emr_api_port': 3000,
              'emr_api_username': 'admin',
              'emr_api_password': 'test'}
    report = CohortReport.get(config, 1, 2019)
    print(report)