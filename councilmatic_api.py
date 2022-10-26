import requests
import json


class CouncilmaticAPI:
    """
    Class to connect to Councilmatic via API.
    """
    base_url = 'http://ocd.datamade.us/bills/?classification=bill'

    def __init__(self, location, keywords):
        self.location = location.replace(" ", "%20")
        self.keywords = keywords
        self.url = self.base_url + '&from_organization__jurisdiction__name__icontains=' + self.location
    
    def get_loop_num(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            raise ValueError("API call failed")
        data = r.json()
        loop_num = data['meta']['max_page']
        print('loops: ', loop_num)
        return loop_num

    def get_data(self, keyword):
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
        bills_list = []
        for keyword in self.keywords:
            bills = self.get_data(keyword)
            bills_list.extend(bills)
        return bills_list


def get_data_for_location_and_topic(location, keywords):
    all_bills = []

    api_call = CouncilmaticAPI(location, keywords)
    bills = api_call.iterate_through_keywords()
    all_bills.extend(bills)

    return all_bills

