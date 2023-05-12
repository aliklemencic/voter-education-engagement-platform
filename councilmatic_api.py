'''
API to connect to Councilmatic.
'''
import requests


class CouncilmaticAPI:
    '''
    Class to connect to Councilmatic via API.
    '''
    base_url = 'http://ocd.datamade.us/events/?classification=bill'

    def __init__(self, location, keywords):
        '''
        Initializes an instance of the `CouncilmaticAPI` class.

        Inputs:
            - location (str): the state or county to get bills for
            - keywords (list of str): the keywords to search for
        '''
        self.location = location.replace(" ", "%20")
        self.keywords = keywords
        self.url = self.base_url + '&from_organization__jurisdiction__name__icontains=' + self.location
    
    def get_loop_num(self, url):
        '''
        Determines how many API calls are required to get all data.
        Raises an error if unable to connect to the API.

        Inputs:
            - url (str): the url to scrape
        
        Returns: (int) the number of loops
        '''
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError("API call failed")
        data = r.json()
        loop_num = data['meta']['max_page']
        print('loops: ', loop_num)
        return loop_num

    def get_data(self, keyword):
        '''
        Retrieves all bills related to a given keyword.
        
        Inputs:
            - keyword (str): the keyword to search for

        Returns: (list of dicts) list of relevant bill information
        '''
        issue_path = '&title__icontains='
        url = self.url + issue_path + keyword
        loops = self.get_loop_num(url)
        bill_list = []

        for i in range(loops):
            page = i + 1
            print('page: ', page)
            r = requests.get(url + '&page=' + str(page))
            if r.status_code != 200:
                break
            bills = r.json()
            bill_list.extend(bills['results'])
        
        return bill_list

    def iterate_through_keywords(self):
        '''
        Iterates through all given keywords to find related bills.

        Inputs: None

        Returns: (list of dicts) list of bill information
        '''
        bills_list = []
        for keyword in self.keywords:
            bills = self.get_data(keyword)
            bills_list.extend(bills)
        return bills_list


def get_data_for_location_and_topic(location, keywords):
    '''
    Creates an instance of `CouncilmaticAPI` and retrieves all 
    bills for the given location and keywords.

    Inputs:
        - location (str): the state or county to get bills for
        - keywords (list of str): the keywords to search for

    Returns: (list of dicts) list of bill information
    '''
    all_bills = []

    api_call = CouncilmaticAPI(location, keywords)
    bills = api_call.iterate_through_keywords()
    all_bills.extend(bills)

    return all_bills
