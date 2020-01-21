from .api_client import ApiClient

import datetime
import logging

LOGGER = logging.getLogger(__name__)

HIV_PROGRAM_ID = 1  # Program ID for HIV in EMR-API

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
        uri = f'programs/{HIV_PROGRAM_ID}/reports/cohort'
        return ApiClient(config).get(uri, name=f'Q{quarter}-{year}',
                                          start_date=start_date,
                                          end_date=end_date)

class MohDisaggregatedReport:
    name = 'MOH Disaggregated Report'
    AGE_GROUPS = [
        '50 plus years',
        '45-49',
        '40-44',
        '35-39',
        '30-34',
        '25-29',
        '20-24',
        '18-19',
        '15-17',
        '10-14',
        '5-9',
        '2-4',
        '12-23 months',
        '6-11 months',
        '0-5 months',
        'Pregnant',
        'Breastfeeding',
    ]

    @staticmethod
    def get(config, quarter, year):
        '''Retrieve quarterly MOH disaggregated cohort report for a given year.'''
        import datetime

        LOGGER.debug(f'Retrieving MOH disaggregated report for Q{quarter}-{year}')
        date = str(datetime.datetime.today())

        report = []
        for age_group in MohDisaggregatedReport.AGE_GROUPS:
            LOGGER.debug(f'Retrieving indicator {age_group}...')
            indicator = ApiClient(config).get('cohort_disaggregated', quarter=f'Q{quarter}-{year}',
                                                                      age_group=age_group,
                                                                      rebuild_outcome=False,
                                                                      initialize=True,
                                                                      program_id=HIV_PROGRAM_ID,
                                                                      date=date)
            if indicator is not None and not indicator:
                # EMR-API returns some records that are completely blank in cases
                # where there are not patients in the given age group.
                indicator[age_group] = {}

            report.append(indicator)

        return report


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

