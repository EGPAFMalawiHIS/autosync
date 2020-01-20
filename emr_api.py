
class CohortReport:
    name = 'Cohort'

    @staticmethod
    def get(api_url, quarter, year):
        '''Retrieve quarterly cohort report for a given year.
        
        Parameters:
            api_url {string} - is the url to the EMR API
            quarter {integer} - is a value in range [1, 4] representing a quarter of a year
            year {integer} - is the year the report is targeting
        '''
        pass

class MohDisaggregatedReport:
    name = 'MOH Disaggregated Report'

    @staticmethod
    def get(api_url, quarter, year):
        '''Retrieve quarterly MOH disaggregated cohort report for a given year.
        
        Parameters:
            api_url {string} - is the url to the EMR API
            quarter {integer} - is a value in range [1, 4] representing a quarter of a year
            year {integer} - is the year the report is targeting
        '''
        pass

class PepfarDisaggregatedReport:
    name = 'PEPFAR Disaggregated Report'

    @staticmethod
    def get(api_url, quarter, year):
        '''Retrieve quarterly PEPFAR disaggregated cohort report for a given year.
        
        Parameters:
            api_url {string} - is the url to the EMR API
            quarter {integer} - is a value in range [1, 4] representing a quarter of a year
            year {integer} - is the year the report is targeting
        '''
        pass

def reports():
    '''Returns a list of all EMR API reports.'''
    return [CohortReport, MohDisaggregatedReport, PepfarDisaggregatedReport]
